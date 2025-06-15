import redis.asyncio as redis
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('[Redis PubSub]')

r = redis.Redis()
pubsub = r.pubsub()

async def publish_incident(incident):
    """
    Publish an incident to the 'incident_queue' channel.
    
    Args:
        incident (dict): The incident data to publish
    """
    logger.info("Publishing incident %s - %s", incident["number"], incident["short_description"])
    await r.publish("incident_queue", json.dumps(incident))

async def subscribe_to_incidents():
    """
    Subscribe to the 'incident_queue' channel.
    
    Returns:
        redis.client.PubSub: The pubsub object that can be used to listen for messages
    """
    logger.info("Subscribing to incident_queue...")
    await pubsub.subscribe("incident_queue")
    return pubsub