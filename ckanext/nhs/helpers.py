import ckan.logic as logic
import ckan.model as model
from ckan.common import config, is_flask_request, c, request
from ckan.plugins import toolkit
import logging
log = logging.getLogger(__name__)

def _get_action(action, context_dict, data_dict):
    return toolkit.get_action(action)(context_dict, data_dict)


def get_resources_list(dataset_id):
    context = {}
    # Using package_show instead of package_search
    pkg = _get_action('package_show', context, {'id':dataset_id})
    resources = pkg['resources']
    filtered_resource = []
    # Filtering resources having data dictionary
    for res in resources:
        try:
            rec = _get_action(u'datastore_search',None, {
                    u'resource_id': res['id'],
                    u'limit': 0
                }
            )
            filtered_resource.append(res)
        except (toolkit.ObjectNotFound, toolkit.NotAuthorized):
            pass
    sorted_resources = sorted(filtered_resource, key=lambda x: x['created'], reverse=True)
    return sorted_resources


def get_resource_list_dropdown(dataset_id):

    resources = get_resources_list(dataset_id)

    return [{'name': x['id'], 'value': x['name']} for x in resources]


def get_dataset_data_dictionary(dataset_id):
    context = {}
    pkg = _get_action('package_show', context, {'id': dataset_id})
    # Filter only resources having datastore_active
    filtered_resource = [i for i in pkg['resources'] if i['datastore_active']]
    sorted_resources = sorted(filtered_resource, key=lambda x: x['last_modified'], reverse=True)
    try:
        if sorted_resources:
            rec = _get_action(u'datastore_search',None, {
                            u'resource_id': sorted_resources[0]['id'],
                            u'limit': 0
                        }
                    )
            return [f for f in rec[u'fields'] if not f[u'id'].startswith(u'_')]
        else:
            return []
    except (toolkit.ObjectNotFound, toolkit.NotAuthorized):
        return []