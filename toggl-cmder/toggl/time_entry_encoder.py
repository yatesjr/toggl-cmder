from json import JSONEncoder

from toggl import time_entry

class TimeEntryEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, time_entry.TimeEntry):
            return { 'time_entry' :
                         {
                             'pid': o.project_id,
                             'description': o.description,
                             'start': o.start_time.isoformat(),
                             'tag': o.tags,
                             'created_with': 'toggl_cmder'
                         }}
        return super(TimeEntryEncoder, self).default(o)
