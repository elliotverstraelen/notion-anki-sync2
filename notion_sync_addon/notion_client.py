"""Notion data models."""
from __future__ import annotations

import time
from pathlib import Path
from typing import Dict, Optional

import requests

from .helpers import get_logger


class NotionClientException(Exception):
    """Notion client exception."""


class NotionClient:
    """Notion client."""

    #: Notion enqueue task endpoint
    NOTION_ENQUEUE_TASK_ENDPOINT: str = (
        'https://www.notion.so/api/v3/enqueueTask'
    )
    #: Notion API get task endpoint
    NOTION_GET_TASK_ENDPOINT: str = 'https://www.notion.so/api/v3/getTasks'
    #: Maximum attempts to get a task (increase for larger tasks)
    NOTION_MAX_RETRIES: int = 600
    #: Notion API retry time, sec
    NOTION_RETRY_TIME: int = 1

    def __init__(self, token: str, debug: bool = False) -> None:
        """Init the client.

        :param token: Notion v2 token
        :param debug: debug mode
        """
        self.logger = get_logger(self.__class__.__name__, debug)
        self.cookies: Dict[str, str] = {'token_v2': token}

    def enqueue_export_task(
        self, page_id: str, recursive: bool = False
    ) -> str:
        """Enqueue an export task for a given page.

        :param page_id: page id
        :param recursive: use recursive export
        :returns: task id
        """
        payload = {
            'task': {
                'eventName': 'exportBlock',
                'request': {
                    'blockId': page_id,
                    'recursive': recursive,
                    'exportOptions': {
                        'exportType': 'html',
                        'timeZone': 'Europe/Moscow',
                        'locale': 'en',
                    },
                },
            }
        }
        attempts_count = 0
        data = None
        while attempts_count < self.NOTION_MAX_RETRIES:
            try:
                resp = requests.post(
                    self.NOTION_ENQUEUE_TASK_ENDPOINT,
                    json=payload,
                    cookies=self.cookies,
                )
            except requests.exceptions.RequestException as exc:
                raise NotionClientException('Request error') from exc
            if resp.status_code == 401:
                self.logger.error('Invalid token')
                raise NotionClientException('Invalid token')
            elif resp.status_code >= 500:
                attempts_count += 1
                self.logger.error(
                    'Notion server error, retrying in %s (%s)',
                    self.NOTION_RETRY_TIME,
                    f'{attempts_count} of {self.NOTION_MAX_RETRIES}',
                )
                time.sleep(self.NOTION_RETRY_TIME)
            else:
                data = resp.json()
                break
        if not data:
            self.logger.error('Cannot submit export task')
            raise NotionClientException('Cannot submit export task')
        task_id = data['taskId']
        self.logger.info(
            'Export task posted: page_id=%s, recursive=%s, task_id=%s',
            page_id,
            recursive,
            task_id,
        )
        return task_id

    def get_task_result(self, task_id: str) -> Optional[str]:
        """Get result of the selected task.

        :param task_id: task id
        :returns: task result
        """
        attempts_count = 0
        while attempts_count < self.NOTION_MAX_RETRIES:
            try:
                resp = requests.post(
                    self.NOTION_GET_TASK_ENDPOINT,
                    json={'taskIds': [task_id]},
                    cookies=self.cookies,
                )
            except requests.exceptions.RequestException as exc:
                raise NotionClientException('Request error') from exc
            data = resp.json()
            self.logger.debug('Got response for task %s: %s', task_id, data)
            if 'results' in data:
                results = data['results'][0]
                if 'error' in results:
                    raise NotionClientException(results['error'])
                if 'status' in results:
                    status = results['status']
                    type_ = status['type']
                    if type_ == 'complete':
                        return status['exportURL']
            attempts_count += 1
            self.logger.debug(
                'Task not ready, retrying in %s (%s)',
                self.NOTION_RETRY_TIME,
                f'{attempts_count} of {self.NOTION_MAX_RETRIES}',
            )
            time.sleep(self.NOTION_RETRY_TIME)
        self.logger.error('Cannot get task result')
        raise NotionClientException('Cannot get task result')

    def export_page(
        self, page_id: str, destination: Path, recursive: bool = False
    ) -> None:
        """Export a page to a zip-file.

        :param page_id: page id
        :param destination: zip-file destination
        :param recursive: recursive
        """
        # Enqueue task
        task_id = self.enqueue_export_task(page_id, recursive=recursive)
        # Get task result
        if task_id:
            export_url = self.get_task_result(task_id)
            if export_url:
                self.logger.info(
                    'Export complete, downloading file on URL: %s',
                    export_url,
                )
                with requests.get(export_url, stream=True) as r:
                    r.raise_for_status()
                    with open(destination, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
