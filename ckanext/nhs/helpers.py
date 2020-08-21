import ckan.logic as logic
import ckan.model as model
from ckan.common import config, is_flask_request, c, request
from ckan.plugins import toolkit
import logging
log = logging.getLogger(__name__)

def _get_action(action, context_dict, data_dict):
    return toolkit.get_action(action)(context_dict, data_dict)


def get_resources_list(dataset_id, has_data_dict=True):
    context = {}
    # Using package_show instead of package_search
    pkg = _get_action('package_show', context, {'id':dataset_id})
    resources = pkg['resources']
    if not has_data_dict:
        return resources
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


import json
def get_dataset_data_dictionary(pkg_dict):
    '''Returns an array of fields as per fields attribute in Table Schema.

    We expect packages / datasets to have a field (in extras) called
    'tableschema' with Frictionless Data Table Schema.
    '''
    if not pkg_dict:
        return []
    tableschema = [ f['value'] for f in pkg_dict.get('extras', []) if f['key'] == 'tableschema' ]
    if tableschema:
        return json.loads(tableschema[0])['fields']
    else:
        return []


def get_latest_themes():
    context = {}
    themes = _get_action('organization_list', context, {'all_fields': True})[:5]
    themes.sort(key=lambda x: x['created'], reverse=True)

    return themes

def get_latest_datasets():
    context = {}
    data_dict = {
        'sort': 'metadata_created desc',
        'rows': 5,
        'facet': False
    }

    datasets = _get_action('package_search', context, data_dict)['results']

    return datasets

def get_latest_resources():
    context = {}
    data_dict = {
        'query': 'name:',
        #'limit': 100,
        #'order_by': 'last_updated'
    }

    resources = _get_action('resource_search', context, data_dict)['results']

    from operator import itemgetter
    resources_sorted = sorted(resources, key=itemgetter('last_modified','created'), reverse=True) 

    return resources_sorted[:5]

def get_cookie_control_config():

        cookie_control_config = {}

        api_key = config.get(
            'ckanext.nhs.cc.api_key', '')
        cookie_control_config['api_key'] = api_key

        license_type = config.get(
            'ckanext.nhs.cc.license_type', '')
        cookie_control_config['license_type'] = license_type

        popup_position = config.get(
            'ckanext.nhs.cc.popup_position', '')
        cookie_control_config['popup_position'] = popup_position

        theme_color = config.get(
            'ckanext.nhs.cc.theme_color', '')
        cookie_control_config['theme_color'] = theme_color

        initial_state = config.get(
            'ckanext.nhs.cc.initial_state', '')
        cookie_control_config['initial_state'] = initial_state

        return cookie_control_config

def get_googleanalytics_config():

    googleanalytics_config = {}

    googleanalytics_id = config.get(
        'googleanalytics.id', '')
    googleanalytics_config['googleanalytics_id'] = googleanalytics_id

    return googleanalytics_config
