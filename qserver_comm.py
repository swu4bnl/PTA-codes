from bluesky_queueserver_api import BPlan
from bluesky_queueserver_api.http import REManagerAPI


# server URL and port edited by BR 6/16/26
qs = REManagerAPI(http_server_uri="https://xf06bm-bmm-qs1.nsls2.bnl.gov:443")
# with open("/nsls2/data/cms/shared/config/agent_runtime/qserver_http_api_keys/BMM_API_KEY_20241101", "r") as f:

## need a new key for the new server  -BR, 6/16/26
with open("/nsls2/data/cms/shared/config/agent_runtime/qserver_http_api_keys/BMM_API_KEY_20260715", "r") as f:
    api_key = f.read().strip()

qs.set_authorization_key(api_key=api_key)
qs.ping()


def single_plan_per(composition, distance, time, scantype, priority: Literal["front", "back"]):
    """Adds one single plan to the queue that assumes BMM is measuring all edges.
    The plan should have the form:
    def plan(composition, distance, time)

    Kwargs instead of args can also be used, but the the BPlan assembly should reflect that.
    The BMM plan will digest these conceptual variables and convert them into motor positions and edges, and mono adjustments.
    """
    plan = BPlan('CMS_driven_measurement', composition, distance, time, scantype)
    qs.item_add(plan, pos=priority)


def chengchu_send_exafs_list(index_list, element, priority='back'):
    for index in index_list:
        name = qs.history_get()['items'][index]['name']
        composition = qs.history_get()['items'][index]['args'][0]
        distance = qs.history_get()['items'][index]['args'][1]
        time = qs.history_get()['items'][index]['args'][2]

        chengchu_plan = BPlan(name, composition, distance, time, 'exafs', element)
        qs.item_add(chengchu_plan, pos=priority)



ELEMENT_LIST = ...


def several_plans_per(composition, distance, time, priority: Literal["front", "back"] = "front"):
    """Adds several plans to the queue that assumes BMM using the priority only to adjust the first, and
    placing all other edges at the back of the queue.
    The plan should have the form:
    def plan(composition, distance, time, *, element="DEFAULT")

    Kwargs instead of args can also be used throughout, but the the BPlan assembly should reflect that.
    The BMM plan will digest these conceptual variables and convert them into motor positions and edges, and mono adjustments.
    """
    plan = BPlan('CMS_driven_measurement', composition, distance, time, element=ELEMENT_LIST[0])
    qs.item_add(plan, pos=priority)
    for element in ELEMENT_LIST[1:]:
        plan = BPlan('CMS_driven_measurement', composition, distance, time, element=element)
        qs.item_add(plan, pos="back")