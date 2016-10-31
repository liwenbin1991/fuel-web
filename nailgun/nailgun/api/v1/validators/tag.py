# -*- coding: utf-8 -*-

#    Copyright 2016 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from nailgun.api.v1.validators.base import BasicValidator
from nailgun.api.v1.validators.json_schema import tag

from nailgun import errors
from nailgun import objects


class TagValidator(BasicValidator):

    single_schema = tag.TAG_CREATION_SCHEMA

    @classmethod
    def validate_delete(cls, data, instance):
        if instance.read_only:
            raise errors.CannotDelete(
                "Read-only tag '{}' cannot be deleted.".format(instance.tag)
            )

        n_ids = [str(n)
                 for n in objects.TagCollection.get_tag_nodes_ids(instance)]

        if n_ids:
            raise errors.CannotDelete(
                "Tag {} is assigned to nodes '{}'.".format(instance.id,
                                                           ",".join(n_ids))
            )

    @classmethod
    def validate_update(cls, data, instance):
        parsed = cls.validate(data, instance=instance)
        if instance.read_only:
            raise errors.CannotUpdate(
                "Read-only tag '{}' cannot be deleted.".format(instance.tag)
            )
        return parsed

    @classmethod
    def validate_create(cls, data, instance):
        parsed = cls.validate(data, instance=instance)
        return parsed

    @classmethod
    def validate_assign(cls, data, instance):
        """Validates tags assignment.

        :param data: Json string with tag ids
        :type data: string
        :param instance: A node instance
        :type node: nailgun.db.sqlalchemy.models.node.Node
        """
        if not instance.cluster:
            raise errors.NotAllowed("Node '{}' is not in a cluster."
                                    "".format(instance.id))
        parsed = super(TagValidator, cls).validate(data)

        for t in parsed:
            if not isinstance(t, int):
                raise errors.InvalidData(
                    "Tag '{}' can not be assigned to the node '{}' as only "
                    "a numeric notation is supported.".format(t, instance.id)
                )
        return parsed

    @classmethod
    def validate(cls, data, instance=None):
        parsed = super(TagValidator, cls).validate(data)
        cls.validate_schema(parsed, cls.single_schema)
        return parsed