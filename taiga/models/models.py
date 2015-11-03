import datetime
from .base import InstanceResource, ListResource


class CommentableReosource(InstanceResource):

    def add_comment(self, comment):
        return self.update(comment=comment)


class CustomAttributeResource(InstanceResource):

    def set_attribute(self, id, value, version=1):
        attributes = self._get_attributes(cache=True)
        formatted_id = '{0}'.format(id)
        attributes['attributes_values'][formatted_id] = value
        response = self.requester.patch(
            '/{endpoint}/custom-attributes-values/{id}',
            endpoint=self.endpoint, id=self.id,
            payload={
                'attributes_values': attributes['attributes_values'],
                'version': version
            }
        )
        return response.json()

    def _get_attributes(self, cache=False):
        response = self.requester.get(
            '/{endpoint}/custom-attributes-values/{id}',
            endpoint=self.endpoint, id=self.id, cache=cache
        )
        return response.json()

    def get_attributes(self):
        return self._get_attributes()


class CustomAttribute(InstanceResource):

    repr_attribute = 'name'

    allowed_params = [
        'name', 'description', 'order', 'project'
    ]


class CustomAttributes(ListResource):

    def create(self, project, name, **attrs):
        attrs.update(
            {
                'project': project, 'name': name
            }
        )
        return self._new_resource(payload=attrs)


class User(InstanceResource):

    endpoint = 'users'

    repr_attribute = 'full_name'

    def starred_projects(self):
        response = self.requester.get(
            '/{endpoint}/{id}/starred', endpoint=self.endpoint,
            id=self.id
        )
        return Projects.parse(self.requester, response.json())


class Users(ListResource):

    instance = User


class Membership(InstanceResource):

    endpoint = 'memberships'

    allowed_params = ['email', 'role', 'project']

    repr_attribute = 'email'


class Memberships(ListResource):

    instance = Membership

    def create(self, project, email, role, **attrs):
        attrs.update({'project': project, 'email': email, 'role': role})
        return self._new_resource(payload=attrs)


class Priority(InstanceResource):

    endpoint = 'priorities'

    allowed_params = ['name', 'color', 'order', 'project']

    repr_attribute = 'name'


class Priorities(ListResource):

    instance = Priority

    def create(self, project, name, **attrs):
        attrs.update({'project': project, 'name': name})
        return self._new_resource(payload=attrs)


class Attachment(InstanceResource):

    repr_attribute = 'subject'

    allowed_params = [
        'object_id', 'project', 'attached_file',
        'description', 'is_deprecated'
    ]


class Attachments(ListResource):

    def create(self, project, object_id, attached_file, **attrs):
        attrs.update({'project': project, 'object_id': object_id})
        return self._new_resource(
            files={'attached_file': open(attached_file, 'rb')},
            payload=attrs
        )


class UserStoryAttachment(Attachment):

    endpoint = 'userstories/attachments'


class UserStoryAttachments(Attachments):

    instance = UserStoryAttachment


class UserStory(CustomAttributeResource, CommentableReosource):

    endpoint = 'userstories'

    repr_attribute = 'subject'

    allowed_params = [
        'assigned_to', 'backlog_order', 'blocked_note', 'version',
        'client_requirement', 'description', 'is_archived', 'is_blocked',
        'is_closed', 'kanban_order', 'milestone', 'points', 'project',
        'sprint_order', 'status', 'subject', 'tags', 'team_requirement',
        'watchers'
    ]

    def add_task(self, subject, status, **attrs):
        return Tasks(self.requester).create(
            self.project, subject, status,
            user_story=self.id, **attrs
        )

    def list_tasks(self):
        return Tasks(self.requester).list(user_story=self.id)

    def list_attachments(self):
        return UserStoryAttachments(self.requester).list(object_id=self.id)

    def attach(self, attached_file, **attrs):
        return UserStoryAttachments(self.requester).create(
            self.project, self.id,
            attached_file, **attrs
        )


class UserStories(ListResource):

    instance = UserStory

    def create(self, project, subject, **attrs):
        attrs.update({'project': project, 'subject': subject})
        return self._new_resource(payload=attrs)

    def import_(self, project, subject, status, **attrs):
        attrs.update(
            {
                'project': project,
                'subject': subject,
                'status': status
            }
        )
        response = self.requester.post('/{endpoint}/{id}/{type}',
                                       endpoint="importer", id=project,
                                       type="us", payload=attrs)
        return self.instance.parse(self.requester, response.json())


class UserStoryStatus(InstanceResource):

    repr_attribute = 'subject'

    endpoint = 'userstory-statuses'

    allowed_params = [
        'color', 'is_closed', 'name', 'order', 'project', 'wip_limit'
    ]


class UserStoryStatuses(ListResource):

    instance = UserStoryStatus

    def create(self, project, name, **attrs):
        attrs.update({'project': project, 'name': name})
        return self._new_resource(payload=attrs)


class Point(InstanceResource):

    endpoint = 'points'

    repr_attribute = 'subject'

    allowed_params = ['color', 'value', 'name', 'order', 'project']


class Points(ListResource):

    instance = Point

    def create(self, project, name, value, **attrs):
        attrs.update({'project': project, 'name': name, 'value': value})
        return self._new_resource(payload=attrs)


class Milestone(InstanceResource):

    endpoint = 'milestones'

    allowed_params = [
        'name', 'project', 'estimated_start', 'estimated_finish',
        'disponibility', 'slug', 'order', 'watchers'
    ]

    parser = {
        'user_stories': UserStories,
    }

    def stats(self):
        response = self.requester.get(
            '/{endpoint}/{id}/stats',
            endpoint=self.endpoint, id=self.id
        )
        return response.json()


class Milestones(ListResource):

    instance = Milestone

    def create(self, project, name, estimated_start,
               estimated_finish, **attrs):
        if isinstance(estimated_start, datetime.datetime):
            estimated_start = estimated_start.strftime('%Y-%m-%d')
        if isinstance(estimated_finish, datetime.datetime):
            estimated_finish = estimated_finish.strftime('%Y-%m-%d')
        attrs.update({
            'project': project,
            'name': name,
            'estimated_start': estimated_start,
            'estimated_finish': estimated_finish
        })
        return self._new_resource(payload=attrs)

    def import_(self, project, name, estimated_start,
                estimated_finish, **attrs):
        if isinstance(estimated_start, datetime.datetime):
            estimated_start = estimated_start.strftime('%Y-%m-%d')
        if isinstance(estimated_finish, datetime.datetime):
            estimated_finish = estimated_finish.strftime('%Y-%m-%d')
        attrs.update({
            'project': project,
            'name': name,
            'estimated_start': estimated_start,
            'estimated_finish': estimated_finish
        })
        response = self.requester.post('/{endpoint}/{id}/{type}',
                                       endpoint="importer", id=project,
                                       type="milestone", payload=attrs)
        return self.instance.parse(self.requester, response.json())


class TaskStatus(InstanceResource):

    endpoint = 'task-statuses'

    allowed_params = ['name', 'color', 'order', 'project', 'is_closed']


class TaskStatuses(ListResource):

    instance = TaskStatus

    def create(self, project, name, **attrs):
        attrs.update({'project': project, 'name': name})
        return self._new_resource(payload=attrs)


class TaskAttachment(Attachment):

    endpoint = 'tasks/attachments'


class TaskAttachments(Attachments):

    instance = TaskAttachment


class Task(CustomAttributeResource, CommentableReosource):

    endpoint = 'tasks'

    repr_attribute = 'subject'

    allowed_params = [
        'assigned_to', 'blocked_note', 'description', 'version',
        'is_blocked', 'is_closed', 'milestone', 'project', 'user_story',
        'status', 'subject', 'tags', 'us_order', 'taskboard_order',
        'is_iocaine', 'external_reference', 'watchers'
    ]

    def list_attachments(self):
        return TaskAttachments(self.requester).list(object_id=self.id)

    def attach(self, attached_file, **attrs):
        return TaskAttachments(self.requester).create(
            self.project, self.id,
            attached_file, **attrs
        )


class Tasks(ListResource):

    instance = Task

    def create(self, project, subject, status, **attrs):
        attrs.update(
            {
                'project': project, 'subject': subject,
                'status': status
            }
        )
        return self._new_resource(payload=attrs)

    def import_(self, project, subject, status, **attrs):
        attrs.update(
            {
                'project': project,
                'subject': subject,
                'status': status
            }
        )
        response = self.requester.post('/{endpoint}/{id}/{type}',
                                       endpoint="importer", id=project,
                                       type="task", payload=attrs)
        return self.instance.parse(self.requester, response.json())


class IssueType(InstanceResource):

    endpoint = 'issue-types'

    allowed_params = ['name', 'color', 'order', 'project']


class IssueTypes(ListResource):

    instance = IssueType

    def create(self, project, name, **attrs):
        attrs.update({'project': project, 'name': name})
        return self._new_resource(payload=attrs)


class IssueStatus(InstanceResource):

    endpoint = 'issue-statuses'

    allowed_params = ['name', 'color', 'order', 'project', 'is_closed']


class IssueStatuses(ListResource):

    instance = IssueStatus

    def create(self, project, name, **attrs):
        attrs.update({'project': project, 'name': name})
        return self._new_resource(payload=attrs)


class IssueAttachment(Attachment):

    endpoint = 'issues/attachments'


class IssueAttachments(Attachments):

    instance = IssueAttachment


class Issue(CustomAttributeResource, CommentableReosource):
    """Issue model

    :param requester: :class:`Requester` instance
    :param assigned_to: :class:`User` id this issue is assigned to
    :param description: description of the issue
    :param is_blocked: set if this issue is blocked or not
    :param milestone: :class:`Milestone` id
    :param project: :class:`Project` id
    :param status: :class:`Status` id
    :param severity: class:`Severity` id
    :param priority: class:`Priority` id
    :param type: class:`Type` id
    :param subject: subject of the issue
    :param tags: array of tags
    :param watchers: array of watchers id

    """

    endpoint = 'issues'

    repr_attribute = 'subject'

    allowed_params = [
        'assigned_to', 'blocked_note', 'description', 'version',
        'is_blocked', 'is_closed', 'milestone', 'project', 'status',
        'severity', 'priority', 'type', 'subject', 'tags', 'watchers',
    ]

    def list_attachments(self):
        return IssueAttachments(self.requester).list(object_id=self.id)

    def upvote(self):
        self.requester.post(
            '/{endpoint}/{id}/upvote',
            endpoint=self.endpoint, id=self.id
        )
        return self

    def downvote(self):
        self.requester.post(
            '/{endpoint}/{id}/downvote',
            endpoint=self.endpoint, id=self.id
        )
        return self

    def attach(self, attached_file, **attrs):
        return IssueAttachments(self.requester).create(
            self.project, self.id,
            attached_file, **attrs
        )


class Issues(ListResource):

    instance = Issue

    def create(self, project, subject, priority, status,
               issue_type, severity, **attrs):
        attrs.update(
            {
                'project': project, 'subject': subject,
                'priority': priority, 'status': status,
                'type': issue_type, 'severity': severity
            }
        )
        return self._new_resource(payload=attrs)

    def import_(self, project, subject, priority, status,
                issue_type, severity, **attrs):
        attrs.update(
            {
                'project': project, 'subject': subject,
                'priority': priority, 'status': status,
                'type': issue_type, 'severity': severity
            }
        )
        response = self.requester.post('/{endpoint}/{id}/{type}',
                                       endpoint="importer", id=project,
                                       type="issue", payload=attrs)
        return self.instance.parse(self.requester, response.json())


class IssueAttribute(CustomAttribute):

    endpoint = 'issue-custom-attributes'


class IssueAttributes(CustomAttributes):

    instance = IssueAttribute


class TaskAttribute(CustomAttribute):

    endpoint = 'task-custom-attributes'


class TaskAttributes(CustomAttributes):

    instance = TaskAttribute


class UserStoryAttribute(CustomAttribute):

    endpoint = 'userstory-custom-attributes'


class UserStoryAttributes(CustomAttributes):

    instance = UserStoryAttribute


class Severity(InstanceResource):

    endpoint = 'severities'

    allowed_params = ['name', 'color', 'order', 'project']


class Severities(ListResource):

    instance = Severity

    def create(self, project, name, **attrs):
        attrs.update({'project': project, 'name': name})
        return self._new_resource(payload=attrs)


class Role(InstanceResource):

    endpoint = 'roles'

    allowed_params = ['name', 'slug', 'order', 'computable']


class Roles(ListResource):

    instance = Role

    def create(self, project, name, **attrs):
        attrs.update({'project': project, 'name': name})
        return self._new_resource(payload=attrs)


class Project(InstanceResource):
    """Taiga project model

    :param requester: :class:`Requester` instance
    :param name: name of the project
    :param description: description of the project
    :param creation_template: base template for the project
    :param is_backlog_activated: name of the project
    :param is_issues_activated: name of the project
    :param is_kanban_activated: name of the project
    :param is_wiki_activated: determines if the project is private or not
    :param is_private: determines if the project is private or not
    :param videoconferences: appear-in or talky
    :param videoconferences_salt: salt videoconference chat url generation
    :param total_milestones: missing
    :param total_story_points: missing

    """

    endpoint = 'projects'

    allowed_params = [
        'name', 'description', 'creation_template',
        'is_backlog_activated', 'is_issues_activated',
        'is_kanban_activated', 'is_private', 'is_wiki_activated',
        'videoconferences', 'videoconferences_salt', 'total_milestones',
        'total_story_points'
    ]

    parser = {
        'members': Users,
        'priorities': Priorities,
        'issue_statuses': IssueStatuses,
        'issue_types': IssueTypes,
        'task_statuses': TaskStatuses,
        'severities': Severities,
        'roles': Roles,
        'points': Points,
        'us_statuses': UserStoryStatuses
    }

    def get_task_by_ref(self, ref):
        """
        Get a :class:`Task` by ref.

        :param ref: :class:`Task` reference
        """
        response = self.requester.get(
            '/{endpoint}/by_ref?ref={task_ref}&project={project_id}',
            endpoint=Task.endpoint,
            task_ref=ref,
            project_id=self.id
        )
        return Task.parse(self.requester, response.json())

    def get_userstory_by_ref(self, ref):
        """
        Get a :class:`UserStory` by ref.

        :param ref: :class:`UserStory` reference
        """
        response = self.requester.get(
            '/{endpoint}/by_ref?ref={us_ref}&project={project_id}',
            endpoint=UserStory.endpoint,
            us_ref=ref,
            project_id=self.id
        )
        return UserStory.parse(self.requester, response.json())

    def get_issue_by_ref(self, ref):
        """
        Get a :class:`Issue` by ref.

        :param ref: :class:`Issue` reference
        """
        response = self.requester.get(
            '/{endpoint}/by_ref?ref={us_ref}&project={project_id}',
            endpoint=Issue.endpoint,
            us_ref=ref,
            project_id=self.id
        )
        return Issue.parse(self.requester, response.json())

    def stats(self):
        """
        Get the stats of the project
        """
        response = self.requester.get(
            '/{endpoint}/{id}/stats',
            endpoint=self.endpoint, id=self.id
        )
        return response.json()

    def like(self):
        """
        Like the project
        """
        self.requester.post(
            '/{endpoint}/{id}/like',
            endpoint=self.endpoint, id=self.id
        )
        return self

    def unlike(self):
        """
        Unlike the project
        """
        self.requester.post(
            '/{endpoint}/{id}/unlike',
            endpoint=self.endpoint, id=self.id
        )
        return self

    def star(self):
        """
        Stars the project
        """
        self.requester.post(
            '/{endpoint}/{id}/star',
            endpoint=self.endpoint, id=self.id
        )
        return self

    def unstar(self):
        """
        Unstars the project
        """
        self.requester.post(
            '/{endpoint}/{id}/unstar',
            endpoint=self.endpoint, id=self.id
        )
        return self

    def add_membership(self, email, role, **attrs):
        """
        Add a Membership to the project and returns a :class:`Membership` resource.

        :param email: email for :class:`Membership`
        :param role: role for :class:`Membership`
        :param attrs: role for :class:`Membership`
        :param attrs: optional :class:`Membership` attributes
        """
        return Memberships(self.requester).create(
            self.id, email, role, **attrs
        )

    def list_memberships(self):
        """
        Get the list of :class:`Membership` resources for the project.
        """
        return Memberships(self.requester).list(project=self.id)

    def add_user_story(self, subject, **attrs):
        """
        Adds a :class:`UserStory` and returns a :class:`UserStory` resource.

        :param subject: subject of the :class:`UserStory`
        :param attrs: other :class:`UserStory` attributes
        """
        return UserStories(self.requester).create(
            self.id, subject, **attrs
        )

    def import_user_story(self, subject, status, **attrs):
        """
        Import an user story and returns a :class:`UserStory` resource.

        :param subject: subject of the :class:`UserStory`
        :param status: status of the :class:`UserStory`
        :param attrs: optional :class:`UserStory` attributes
        """
        return UserStories(self.requester).import_(
            self.id, subject, status, **attrs
        )

    def list_user_stories(self):
        """
        Returns the :class:`UserStory` list of the project.
        """
        return UserStories(self.requester).list(project=self.id)

    def add_issue(self, subject, priority, status,
                  issue_type, severity, **attrs):
        """
        Adds a Issue and returns a :class:`Issue` resource.

        :param subject: subject of the :class:`Issue`
        :param priority: priority of the :class:`Issue`
        :param priority: status of the :class:`Issue`
        :param issue_type: type of the :class:`Issue`
        :param severity: severity of the :class:`Issue`
        :param attrs: optional :class:`Issue` attributes
        """
        return Issues(self.requester).create(
            self.id, subject, priority, status,
            issue_type, severity, **attrs
        )

    def import_issue(self, subject, priority, status,
                     issue_type, severity, **attrs):
        """
        Import and issue and returns a :class:`Issue` resource.

        :param subject: subject of :class:`Issue`
        :param priority: priority of :class:`Issue`
        :param status: status of :class:`Issue`
        :param issue_type: issue type of :class:`Issue`
        :param severity: severity of :class:`Issue`
        :param attrs: optional :class:`Issue` attributes
        """
        return Issues(self.requester).import_(
            self.id, subject, priority, status,
            issue_type, severity, **attrs
        )

    def list_issues(self):
        """
        Returns the :class:`Issue` list of the project.
        """
        return Issues(self.requester).list(project=self.id)

    def add_milestone(self, name, estimated_start, estimated_finish, **attrs):
        """
        Add a Milestone to the project and returns a :class:`Milestone` object.

        :param name: name of the :class:`Milestone`
        :param estimated_start: estimated start time of the :class:`Milestone`
        :param estimated_finish: estimated finish time of the :class:`Milestone`
        :param attrs: optional attributes for :class:`Milestone`
        """
        return Milestones(self.requester).create(
            self.id, name, estimated_start,
            estimated_finish, **attrs
        )

    def import_milestone(self, name, estimated_start, estimated_finish, **attrs):
        """
        Import a Milestone and returns a :class:`Milestone` object.

        :param name: name of the :class:`Milestone`
        :param estimated_start: estimated start time of the :class:`Milestone`
        :param estimated_finish: estimated finish time of the :class:`Milestone`
        :param attrs: optional attributes for :class:`Milestone`
        """
        return Milestones(self.requester).import_(
            self.id, name, estimated_start,
            estimated_finish, **attrs
        )

    def list_milestones(self):
        """
        Get the list of :class:`Milestone` resources for the project.
        """
        return Milestones(self.requester).list(project=self.id)

    def add_point(self, name, value, **attrs):
        """
        Add a Point to the project and returns a :class:`Point` object.

        :param name: name of the :class:`Point`
        :param value: value of the :class:`Point`
        :param attrs: optional attributes for :class:`Point`
        """
        return Points(self.requester).create(self.id, name, value, **attrs)

    def list_points(self):
        """
        Get the list of :class:`Point` resources for the project.
        """
        return Points(self.requester).list(project=self.id)

    def add_task_status(self, name, **attrs):
        """
        Add a Task status to the project and returns a :class:`TaskStatus` object.

        :param name: name of the :class:`TaskStatus`
        :param attrs: optional attributes for :class:`TaskStatus`
        """
        return TaskStatuses(self.requester).create(self.id, name, **attrs)

    def list_task_statuses(self):
        """
        Get the list of :class:`Task` resources for the project.
        """
        return TaskStatuses(self.requester).list(project=self.id)

    def import_task(self, subject, status, **attrs):
        """
        Import a Task and return a :class:`Task` object.

        :param subject: subject of the :class:`Task`
        :param status: status of the :class:`Task`
        :param attrs: optional attributes for :class:`Task`
        """
        return Tasks(self.requester).import_(
            self.id, subject, status
        )

    def add_user_story_status(self, name, **attrs):
        """
        Add a UserStory status to the project and returns a :class:`UserStoryStatus` object.

        :param name: name of the :class:`UserStoryStatus`
        :param attrs: optional attributes for :class:`UserStoryStatus`
        """
        return UserStoryStatuses(self.requester).create(self.id, name, **attrs)

    def list_user_story_statuses(self):
        """
        Get the list of :class:`UserStoryStatus` resources for the project.
        """
        return UserStoryStatuses(self.requester).list(project=self.id)

    def add_issue_type(self, name, **attrs):
        """
        Add a Issue type to the project and returns a :class:`IssueType` object.

        :param name: name of the :class:`IssueType`
        :param attrs: optional attributes for :class:`IssueType`
        """
        return IssueTypes(self.requester).create(self.id, name, **attrs)

    def list_issue_types(self):
        """
        Get the list of :class:`IssueType` resources for the project.
        """
        return IssueTypes(self.requester).list(project=self.id)

    def add_severity(self, name, **attrs):
        """
        Add a Severity to the project and returns a :class:`Severity` object.

        :param name: name of the :class:`Severity`
        :param attrs: optional attributes for :class:`Severity`
        """
        return Severities(self.requester).create(self.id, name, **attrs)

    def list_severities(self):
        """
        Get the list of :class:`Severity` resources for the project.
        """
        return Severities(self.requester).list(project=self.id)

    def add_role(self, name, **attrs):
        """
        Add a Role to the project and returns a :class:`Role` object.

        :param name: name of the :class:`Role`
        :param attrs: optional attributes for :class:`Role`
        """
        return Roles(self.requester).create(self.id, name, **attrs)

    def list_roles(self):
        """
        Get the list of :class:`Role` resources for the project.
        """
        return Roles(self.requester).list(project=self.id)

    def add_priority(self, name, **attrs):
        """
        Add a Priority to the project and returns a :class:`Priority` object.

        :param name: name of the :class:`Priority`
        :param attrs: optional attributes for :class:`Priority`
        """
        return Priorities(self.requester).create(self.id, name, **attrs)

    def list_priorities(self):
        """
        Get the list of :class:`Priority` resources for the project.
        """
        return Priorities(self.requester).list(project=self.id)

    def add_issue_status(self, name, **attrs):
        """
        Add a Issue status to the project and returns a :class:`IssueStatus` object.

        :param name: name of the :class:`IssueStatus`
        :param attrs: optional attributes for :class:`IssueStatus`
        """
        return IssueStatuses(self.requester).create(self.id, name, **attrs)

    def list_issue_statuses(self):
        """
        Get the list of :class:`IssueStatus` resources for the project.
        """
        return IssueStatuses(self.requester).list(project=self.id)

    def add_wikipage(self, slug, content, **attrs):
        """
        Add a Wiki page to the project and returns a :class:`WikiPage` object.

        :param name: name of the :class:`WikiPage`
        :param attrs: optional attributes for :class:`WikiPage`
        """
        return WikiPages(self.requester).create(
            self.id, slug, content, **attrs
        )

    def import_wikipage(self, slug, content, **attrs):
        """
        Import a Wiki page and return a :class:`WikiPage` object.

        :param slug: slug of the :class:`WikiPage`
        :param content: content of the :class:`WikiPage`
        :param attrs: optional attributes for :class:`Task`
        """
        return WikiPages(self.requester).import_(
            self.id, slug, content, **attrs
        )

    def list_wikipages(self):
        """
        Get the list of :class:`WikiPage` resources for the project.
        """
        return WikiPages(self.requester).list(project=self.id)

    def add_wikilink(self, title, href, **attrs):
        """
        Add a Wiki link to the project and returns a :class:`WikiLink` object.

        :param title: title of the :class:`WikiLink`
        :param href: href of the :class:`WikiLink`
        :param attrs: optional attributes for :class:`WikiLink`
        """
        return WikiLinks(self.requester).create(self.id, title, href, **attrs)

    def import_wikilink(self, title, href, **attrs):
        """
        Import a Wiki link and return a :class:`WikiLink` object.

        :param title: title of the :class:`WikiLink`
        :param href: href of the :class:`WikiLink`
        :param attrs: optional attributes for :class:`WikiLink`
        """
        return WikiLinks(self.requester).import_(self.id, title, href, **attrs)

    def list_wikilinks(self):
        """
        Get the list of :class:`WikiLink` resources for the project.
        """
        return WikiLinks(self.requester).list(project=self.id)

    def add_issue_attribute(self, name, **attrs):
        """
        Add a new Issue attribute and return a :class:`IssueAttribute` object.

        :param name: name of the :class:`IssueAttribute`
        :param attrs: optional attributes for :class:`IssueAttribute`
        """
        return IssueAttributes(self.requester).create(
            self.id, name, **attrs
        )

    def list_issue_attributes(self):
        """
        Get the list of :class:`IssueAttribute` resources for the project.
        """
        return IssueAttributes(self.requester).list(project=self.id)

    def add_task_attribute(self, name, **attrs):
        """
        Add a new Task attribute and return a :class:`TaskAttribute` object.

        :param name: name of the :class:`TaskAttribute`
        :param attrs: optional attributes for :class:`TaskAttribute`
        """
        return TaskAttributes(self.requester).create(
            self.id, name, **attrs
        )

    def list_task_attributes(self):
        """
        Get the list of :class:`TaskAttribute` resources for the project.
        """
        return TaskAttributes(self.requester).list(project=self.id)

    def add_user_story_attribute(self, name, **attrs):
        """
        Add a new User Story attribute and return a :class:`UserStoryAttribute` object.

        :param name: name of the :class:`UserStoryAttribute`
        :param attrs: optional attributes for :class:`UserStoryAttribute`
        """
        return UserStoryAttributes(self.requester).create(
            self.id, name, **attrs
        )

    def list_user_story_attributes(self):
        """
        Get the list of :class:`UserStoryAttribute` resources for the project.
        """
        return UserStoryAttributes(self.requester).list(project=self.id)


class Projects(ListResource):

    instance = Project

    def create(self, name, description, **attrs):
        """
        Create a new :class:`Project`

        :param name: name of the :class:`Project`
        :param description: description of the :class:`Project`
        :param attrs: optional attributes for :class:`Project`
        """
        attrs.update({'name': name, 'description': description})
        return self._new_resource(payload=attrs)

    def import_(self, name, description, roles, **attrs):
        attrs.update(
            {
                'name': name,
                'description': description,
                'roles': roles
            }
        )
        response = self.requester.post('/{endpoint}', endpoint="importer",
                                       payload=attrs)
        return self.instance.parse(self.requester, response.json())

    def get_by_slug(self, slug):
        """
        Get a :class:`Project` by slug

        :param slug: the slug of the :class:`Project`
        """
        response = self.requester.get(
            '/{endpoint}/by_slug?slug={slug}',
            endpoint=self.instance.endpoint,
            slug=slug
        )
        return self.instance.parse(self.requester, response.json())


class WikiAttachment(Attachment):

    endpoint = 'wiki/attachments'


class WikiAttachments(Attachments):

    instance = WikiAttachment


class WikiPage(InstanceResource):

    endpoint = 'wiki'

    repr_attribute = 'slug'

    allowed_params = ['project', 'slug', 'content', 'watchers']

    def attach(self, attached_file, **attrs):
        return WikiAttachments(self.requester).create(
            self.project, self.id,
            attached_file, **attrs
        )


class WikiPages(ListResource):

    instance = WikiPage

    def create(self, project, slug, content, **attrs):
        attrs.update({'project': project, 'slug': slug, 'content': content})
        return self._new_resource(payload=attrs)

    def import_(self, project, slug, content, **attrs):
        attrs.update({'project': project, 'slug': slug, 'content': content})
        response = self.requester.post('/{endpoint}/{id}/{type}',
                                       endpoint="importer", id=project,
                                       type="wiki_page", payload=attrs)
        return self.instance.parse(self.requester, response.json())


class WikiLink(InstanceResource):

    endpoint = 'wiki-links'

    repr_attribute = 'title'

    allowed_params = ['project', 'title', 'href', 'order']


class WikiLinks(ListResource):

    instance = WikiLink

    def create(self, project, title, href, **attrs):
        attrs.update({'project': project, 'title': title, 'href': href})
        return self._new_resource(payload=attrs)

    def import_(self, project, title, href, **attrs):
        attrs.update({'project': project, 'title': title, 'href': href})
        response = self.requester.post('/{endpoint}/{id}/{type}',
                                       endpoint="importer", id=project,
                                       type="wiki_link", payload=attrs)
        return self.instance.parse(self.requester, response.json())


class History(InstanceResource):

    def __init__(self, *args, **kwargs):
        super(History, self).__init__(*args, **kwargs)
        self.issue = HistoryIssue(self.requester)
        self.task = HistoryTask(self.requester)
        self.user_story = HistoryUserStory(self.requester)
        self.wiki = HistoryWiki(self.requester)


class HistoryEntity(object):

    endpoint = 'history'

    def __init__(self, requester):
        self.requester = requester

    def get(self, resource_id):
        response = self.requester.get(
            '/{endpoint}/{entity}/{id}',
            endpoint=self.endpoint, entity=self.entity, id=resource_id
        )
        return response.json()

    def delete_comment(self, resource_id, ent_id):
        self.requester.post(
            '/{endpoint}/{entity}/{id}/delete_comment?id={ent_id}',
            endpoint=self.endpoint, entity=self.entity,
            id=resource_id, ent_id=ent_id
        )

    def undelete_comment(self, resource_id, ent_id):
        self.requester.post(
            '/{endpoint}/{entity}/{id}/undelete_comment?id={ent_id}',
            endpoint=self.endpoint, entity=self.entity,
            id=resource_id, ent_id=ent_id
        )


class HistoryIssue(HistoryEntity):

    def __init__(self, *args, **kwargs):
        super(type(self), self).__init__(*args, **kwargs)
        self.entity = 'issue'


class HistoryTask(HistoryEntity):

    def __init__(self, *args, **kwargs):
        super(type(self), self).__init__(*args, **kwargs)
        self.entity = 'task'


class HistoryUserStory(HistoryEntity):

    def __init__(self, *args, **kwargs):
        super(type(self), self).__init__(*args, **kwargs)
        self.entity = 'userstory'


class HistoryWiki(HistoryEntity):

    def __init__(self, *args, **kwargs):
        super(type(self), self).__init__(*args, **kwargs)
        self.entity = 'wiki'
