from requests.auth import HTTPBasicAuth
import requests, json

from toggl import workspace_decoder
from toggl import workspace

from toggl import project_decoder
from toggl import project_encoder
from toggl import project

from toggl import tag_decoder
from toggl import tag_encoder
from toggl import tag

from toggl import time_entry_decoder
from toggl import time_entry_encoder
from toggl import time_entry

from toggl import user

class Interface(object):
    def __init__(self, **kwargs):
        super(Interface, self).__init__()

        self.__logger = kwargs.get('logger')
        self.__auth = HTTPBasicAuth(kwargs['api_token'], 'api_token')

    def test_connection(self):
        reply = requests.get(user.User.api_url(),
                             auth=self.__auth)
        if reply.reason == 'Forbidden':
            return False
        return True

    def reset_user_token(self):
        reply = requests.post(user.User.api_token_reset_url(),
                              auth=self.__auth)
        reply.raise_for_status()
        return reply.text

    def download_user_data(self):
        reply = requests.get(
            user.User.api_user_url(),
            auth=self.__auth)
        reply.raise_for_status()

        # json decoder doesn't work properly
        data_block = reply.json()['data']

        user_projects = []
        projects = data_block['projects']
        for p in projects:
            user_projects.append(
                project.Project(
                    name=p['name'],
                    workspace_id=p['wid'],
                    project_id=p['id'],
                    created=p['created_at'],
                    color=p['color'],
                    hex_color=p['hex_color']
                )
            )

        user_workspaces = []
        workspaces = data_block['workspaces']
        for w in workspaces:
            user_workspaces.append(
                workspace.Workspace(
                    id=w['id'],
                    name=w['name'],
                )
            )

        user_tags = []
        tags = data_block['tags']
        for t in tags:
            user_tags.append(
                tag.Tag(
                    id=t['id'],
                    name=t['name'],
                    workspace_id=t['wid'],
                    created=t['at']
                )
            )

        user_time_entries = []
        time_entries = data_block['time_entries']
        for t in time_entries:
            user_time_entries.append(
                time_entry.TimeEntry(
                    id=t['id'],
                    wid=t['wid'],
                    pid=t.get('pid', None),
                    description=t['description'],
                    start=t['start'],
                    stop=t.get('stop', None),
                    duration=t['duration'],
                    tags=t.get('tags', [])
                )
            )

        return user.User(
            id=data_block['id'],
            full_name=data_block['fullname'],
            api_token=data_block['api_token'],
            tags=user_tags,
            time_entries=user_time_entries,
            workspaces=user_workspaces,
            projects=user_projects
        )

    def download_workspaces(self):
        reply =  requests.get(workspace.Workspace.api_url(),
                            auth=self.__auth)
        reply.raise_for_status()
        return json.loads(reply.text,
                          cls=workspace_decoder.WorkspaceDecoder)

    def download_projects(self, incoming_workspace):
        reply = requests.get(incoming_workspace.projects_url,
                             auth=self.__auth)
        reply.raise_for_status()
        projects = []
        for project in json.loads(reply.text,
                                  cls=project_decoder.ProjectDecoder):
            project.workspace = incoming_workspace
            projects.append(project)

        return projects

    def download_tags(self, incoming_workspace):
        reply = requests.get(incoming_workspace.tags_url,
                             auth=self.__auth)
        reply.raise_for_status()
        tags = []
        for tag in json.loads(reply.text,
                              cls=tag_decoder.TagDecoder):
            tag.workspace = incoming_workspace
            tags.append(tag)

        return tags

    def get_current_entry(self):
        reply = requests.get(time_entry.TimeEntry.api_current_entry_url(),
                             auth=self.__auth)
        reply.raise_for_status()
        return json.loads(reply.text,
                          cls=time_entry_decoder.TimeEntryDecoder)

    def create_project(self, project):
        data = json.dumps(project, cls=project_encoder.ProjectEncoder)
        result = requests.post(project.api_url(),
                               data=data,
                               auth=self.__auth)
        result.raise_for_status()

    def create_tag(self, tag):
        data = json.dumps(tag, cls=tag_encoder.TagEncoder)
        result = requests.post(tag.api_url(),
                               data=data,
                               auth=self.__auth)
        result.raise_for_status()

    def start_time_entry(self, time_entry):
        data = json.dumps(time_entry, cls=time_entry_encoder.TimeEntryEncoder)
        result = requests.post(time_entry.api_url(),
                               data=data,
                               auth=self.__auth)
        result.raise_for_status()

    def stop_time_entry(self, time_entry):
        result = requests.put(time_entry.api_stop_entry_url(),
                              auth=self.__auth)
        result.raise_for_status()
