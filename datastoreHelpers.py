# Author: Ren Demeis-Ortiz
# Course: CS493 Cloud Application Development (Final Project)
# Description: Helper functions to interact with googlecloud datastore entities
#
# Sources: OSU CS493 Module 4 Exploration
#          https://canvas.oregonstate.edu/courses/1870359/modules/items/22099651
from google.cloud import datastore
import constants as c
from urllib.parse import urlencode, unquote

client = datastore.Client()


def create_entity(entity_kind, content, entity_id=None):
    """
    Creates Datastore Entity from JSON Request
    
    :params: 
            entity_kind (string) is the type of entity
            content (dict) JSON request content
            entity_id int
            
    :returns: new_entity (datastore entity) datastore entity that was created
    """
    if entity_id:
        new_entity = datastore.Entity(key=client.key(entity_kind, entity_id))
    else:
        new_entity = datastore.Entity(key=client.key(entity_kind))
    new_entity.update(content)
    client.put(new_entity)
    if get_entity("counter", entity_kind):
        increment_counter(entity_kind)

    return new_entity


def get_all(entity_kind, request):
    """
    Gets datastore entities of kind using cursor with limit set in constants

    Must use counter methods with this method
    
    :params: 
            entity_kind (string) is the type of entity
            request (flask request) flask request to pull url information from 
            
    :returns: results (list) of datastore entities, a next link, and a count
    Source: https://canvas.oregonstate.edu/courses/1870359/modules/items/22099648
    """
    query = client.query(kind=entity_kind)
    q_cursor = unquote(request.args.get('cursor', ''))
    result_iterator = query.fetch(limit=c.limit, start_cursor=q_cursor)
    pages = result_iterator.pages
    results = {"next": None,
               "total_" + entity_kind: get_count(entity_kind),
               entity_kind: list(next(pages))}
    if result_iterator.next_page_token:
        args = urlencode({"cursor": result_iterator.next_page_token})
        results["next"] = request.base_url + "?" + args
    else:
        results["next"] = None
    for e in results[entity_kind]:
        add_id_self(e, request, entity_kind)
    return results


def get_filter_query(entity_kind, query_list, request):
    """
    Gets datastore entities of kind with a particular filter and constant limit

    :params:
            entity_kind (string) is the type of entity
            request (flask request) flask request to pull url information from

    :returns: results (list) of datastore entities, a next link, and a count
    Source: https://canvas.oregonstate.edu/courses/1870359/modules/items/22099648
    """
    query = client.query(kind=entity_kind)
    for q in query_list:
        query.add_filter(q["property"], q["operator"], q["value"])
    q_cursor = unquote(request.args.get('cursor', ''))
    result_iterator = query.fetch(limit=c.limit, start_cursor=q_cursor)
    query = client.query(kind=entity_kind)
    for q in query_list:
        query.add_filter(q["property"], q["operator"], q["value"])
    query.keys_only()
    total = len(list(query.fetch()))
    pages = result_iterator.pages
    results = {"next": None,
               "total_" + entity_kind: total,
               entity_kind: list(next(pages))}
    if result_iterator.next_page_token:
        args = urlencode({"cursor": result_iterator.next_page_token})
        results["next"] = request.base_url + "?" + args
    else:
        results["next"] = None
    for e in results[entity_kind]:
        add_id_self(e, request, entity_kind)
    return results


def get_full_collection(entity_kind, request):
    """
    Gets all datastore entities of kind with limit and offset options

    :params:
            entity_kind (string) is the type of entity
            request (flask request) flask request to pull url information from

    :returns: results (list) of datastore entities
    Source: https://canvas.oregonstate.edu/courses/1870359/modules/items/22099648
    """
    query = client.query(kind=entity_kind)
    results = {entity_kind: list(query.fetch())}
    for e in results[entity_kind]:
        add_id_self(e, request, entity_kind)

    return results


def get_entity(entity_kind, entity_id):
    """
    Gets datastore entity with kind and id
    
    :params: 
            entity_kind (string) is the type of entity
            entity_int (int) id of entity to retrieve key
            
    :returns: entity (datastore entity) entity with key
    """
    entity_key = client.key(entity_kind, entity_id)
    entity = client.get(key=entity_key)

    return entity


def get_entity_key(entity_kind, entity_id):
    """

    :param entity_kind: (string) is the type of entity
    :param entity_id: (int) id of entity to retrieve key

    :return: Datastore entity key
    """
    return client.key(entity_kind, entity_id)


def edit_entity(entity, content):
    """
    Edits Datastore Entity from JSON Request
    
    :params: 
            entity (datastore entity) entity to be edited
            content (dict) JSON request content
            
    :returns: If entity doesn't exist returns None
            else returns:
            entity (datastore entity) datastore entity that was edited
    """
    
    if not entity:
        return
        
    for k, v in content.items():
        entity[k] = v
        
    client.put(entity)
    return entity


def delete_entity(entity_kind, entity_id):
    """
    Deletes datastore entity with kind and id
    
    :params: 
            entity_kind (string) is the type of entity
            entity_int (int) id of entity to retrieve key
            
    :returns: None
    """
    entity_key = client.key(entity_kind, entity_id)
    client.delete(entity_key)
    if get_entity("counter", entity_kind):
        decrement_counter(entity_kind)
    
    return None


def edit_property(entity_list, property, new_value):  
    """
    Edits a single property of an entity.
    
    :params: 
            entity_list (list) list of entities who's property is to be changed
            property (string) property you want to change
            new value value to change the property to
            
    :returns: None
    """  
    for e in entity_list:
        if e:
            e[property] = new_value
            client.put(e)
    return None
               
               
def get_add_filter_query(entity_kind, query_list):
    """
    Perfoms datastore query with using add_filter.
    
    :params: 
            entity_kind (string) is the type of entity
            query_list (list) list query add_filter argument in format:
                        [{
                          "property": <property string>, 
                          "operator": <add>, 
                          "value": <value to search for>
                          },
                         { 
                          "property": <property string>, 
                          "operator": <add>, 
                          "value": <value to search for>
                          }]
            
    :returns: results (list) list of query results based on filters
    """    
    query = client.query(kind=entity_kind)
    for q in query_list:
        query.add_filter(q["property"], q["operator"], q["value"])
    results = list(query.fetch())
    for e in results:
        e["id"] = e.key.id
        
    return results


def add_id_self(e, req, entity_kind):
    """
    Adds self and id property to entity

    :params: 
            e (datastore entity) datastore entity
            req (flask request) flask request to pull url information from
            entity_kind (string) is the type of entity

    :returns: datastore entity
    """
    if e.key.id:
        e["id"] = e.key.id
    elif e.key.name:
        e["id"] = e.key.name
    e["self"] = get_self_url(req, entity_kind, e["id"])

    return e


def get_self_url(req, entity_kind, id=""):
    """
    Creates a url to access the resource that has the id passed
    
    :params: 
            req (flask request) flask request to pull url information from
            entity_kind (string) is the type of entity
            id (int) id of entity create link for
            
    :returns: url (string) url to the entity with the given id
    """
    url = req.host_url + entity_kind + "/" + str(id)
    
    return url


def repackage_carrier(entity, request):
    """
    Changes the carrier property to include two properties: self, id.
    
    :params: 
            request (flask request) flask request to pull url information from
            entity (datastore entity) entity to edit carrier property
            
    :returns: entity (datastore entity) entity that was passed
    """
    if not entity["carrier"]:
        return entity
    else:
        carrier_id = entity["carrier"]
        entity["carrier"] = {}
        entity["carrier"]["id"] = carrier_id
        entity["carrier"]["self"] = get_self_url(request, c.boats, carrier_id)
        return entity


def increment_counter(entity_kind):
    """
    Increase counter for number of entities for kind passed

    :params:
            entity_kind (string) is the type of entity

    :returns: None
    """
    e = get_entity("counter", entity_kind)
    e["count"] = e["count"] + 1
    client.put(e)
    return None


def decrement_counter(entity_kind):
    """
    Decrease counter for number of entities for kind passed

    :params:
            entity_kind (string) is the type of entity

    :returns: None
    """
    e = get_entity("counter", entity_kind)
    e["count"] = e["count"] - 1
    client.put(e)
    return None


def get_count(entity_kind):
    """
    Get the number of entities of a certain kind

    :params:
            entity_kind (string) is the type of entity

    :returns:
    """
    e = get_entity("counter", entity_kind)
    return e["count"]


def initialize_counter(entity_kind):
    """
    Create counter for entities in kind

    :params:
            entity_kind (string) type of entity

    :returns: None
    """
    e = get_entity("counter", entity_kind)
    if e:
        query = client.query(kind=entity_kind)
        query.keys_only()
        results = {entity_kind: list(query.fetch())}
        e["count"] = len(results[entity_kind])
        client.put(e)
    else:
        create_entity("counter", {"count": 0}, entity_kind)
    return None


def remove_counter(entity_kind):
    """
    Remove counter for entity type

    :params:
            entity_kind (string) type of entity

    :returns: None
    """
    delete_entity("counter", entity_kind)
    return None
