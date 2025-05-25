from openai import OpenAI
from datetime import datetime
import os, json, random
from tqdm import tqdm

#DSL to function call 
def create_function_list():
    UDrive = {
        "type": "function",
        "function" : {
            "name": "UDrive",
            "description": "UDrive is an event-based Domain-Specific Language designed for specifying autonomous vehicle behaviour. \
                            Specifically, 'trigger' and 'condition' together define the driving environment the vehicle should be in when the rule takes effect, while 'action' describes the driving behavior the ego vehicle should follow in that environment as specified by the rule.",
            "parameters": {
                "type": "object",
                "properties": {
                    "trigger" : {
                        "type": "object",
                        "properties": {
                            "always": {
                                "type": "boolean",
                                "description": "Trigger 'always' ensures that the rule applies to all types of roads."
                            },
                            "in": {
                                "type": "string",
                                "enum": ["urban_lane", "intersection", "bridge", "ferry_crossing", "mountain_road", "icy_road", "flooded_road", "flooded_bridge", "motorway", "railway_crossing", "sharp_curve", "narrow_road", "narrow_bridge", "muddy_road", "non-motorized", "steep_slope", "sharp_bend", "roundabout", "crosswalk", "no_parking_zone", "tunnel", "highway", "highway_exit_ramp"],
                                "description": "Used to specify the type of road the vehicle is driving on when the rule takes effect."
                            },
                            "not_in": {
                                "type": "string",
                                "enum": ["urban_lane", "intersection", "bridge", "ferry_crossing", "mountain_road", "icy_road", "flooded_road", "flooded_bridge", "motorway", "railway_crossing", "sharp_curve", "narrow_road", "narrow_bridge", "muddy_road", "non-motorized", "steep_slope", "sharp_bend", "roundabout", "crosswalk", "no_parking_zone", "tunnel", "highway", "highway_exit_ramp"],
                                "description": "Used to specify the types of roads the vehicle must not be on when the rule takes effect."
                            }
                        },
                        "description": "Used to specify the type of road the vehicle is (or must not be) on when the rule takes effect; only one of (always, in, or not_in) can be used at a time."
                    },
                    "condition": {
                        "type": "object",
                        "properties": {
                            "time_is": {
                                "type": "string",
                                "enum": ["daytime", "night"],
                                "description": "Used to specify whether the rule takes effect during the day or at night; if not set, it applies all day."
                            },
                            "weather_is": {
                                "type": "string",
                                "enum": ["raining", "foggy", "snowing", "sandstorm", "hail"],
                                "description": "Used to specify the weather conditions under which the rule takes effect; if not set, the rule applies in all weather conditions."
                            },
                            "is_special_lane": {
                                "type": "string",
                                "enum": ["fast_lane", "bus_lane", "emergency_lane", "without_centerline", "one_lane_same_direction", "non_motorized"],
                                "description": "It can be used to impose more specific constraints on the current driving lane by specifying that the current driving area is located on a special type of lane. It is typically used in combination with triggers such as 'urban_lane' and 'motorway', which have clearly defined lane markings."
                            },
                            "not_special_lane": {
                                "type": "string",
                                "enum": ["fast_lane", "bus_lane", "emergency_lane", "without_centerline", "one_lane_same_direction", "non_motorized"],
                                "description": "This constraint enables a more precise specification of the current driving lane by indicating that the driving area does not belong to any special lane category, thereby serving as the inverse condition of 'is_special_lane'."
                            },
                            "distance_to": {
                                "type": "object",
                                "properties": {
                                    "road_type": {
                                        "type": "string",
                                        "enum": ["urban_lane", "intersection", "bridge", "ferry_crossing", "mountain_road", "icy_road", "flooded_road", "flooded_bridge", "motorway", "railway_crossing", "sharp_curve", "narrow_road", "narrow_bridge", "muddy_road", "non-motorized", "steep_slope", "sharp_bend", "roundabout", "crosswalk", "no_parking_zone", "tunnel", "highway", "highway_exit_ramp"],
                                        "description": "Used to describe the types of roads that may be encountered ahead."
                                    },
                                    "CompOp": {
                                        "type": "string",
                                        "enum": [">", "<", "==", "<=", ">="],
                                        "description": "Used to specify the type of constraint on the distance to the upcoming road type."
                                    },
                                    "distance_num": {
                                        "type": "number",
                                        "description": "Used to specify a specific distance value that should be generated appropriately."
                                    }
                                },
                                "description": "This is primarily used in scenarios where a change in road type may occur. Specifically, 'road_type' defines the potential upcoming road type, and 'ComOp' along with 'distance' specifies the distance relation between the current vehicle position and the next road type."
                            },
                            "find_obstacle": {
                                "type": "object",
                                "properties": {
                                    "obstacle_type": {
                                        "type": "string",
                                        "enum": ["all", "vehicle", "pedestrian", "bicycle", "motorcycle", "non-motorized", "others"],
                                        "description": "Used to specify the type of obstacle. 'all' represents all types of obstacles, while 'others' refers to obstacles other than 'vehicle', 'pedestrian', 'bicycle', and 'motorcycle'."
                                    },
                                    "position": {
                                        "type": "string",
                                        "enum": ["left", "right", "front", "back"],
                                        "description": "Used to specify the position of the obstacle relative to the ego vehicle."
                                    },
                                    "direction": {
                                        "type": "string",
                                        "enum": ["same", "opposite"],
                                        "description": "An optional setting, used to describe whether the obstacle is moving in the same or opposite direction as the ego vehicle."
                                    },
                                    "distance": {
                                        "type": "object",
                                        "properties": {
                                            "CompOp": {
                                                "type": "string",
                                                "enum": [">", "<", "==", "<=", ">="],
                                                "description": "Used to specify the type of constraint on the distance to the obstacle."
                                            },
                                            "distance_num": {
                                                "type": "number",
                                                "description": "Used to specify a specific distance value that should be generated appropriately."
                                            }
                                        },
                                        "description": "Used to describe the distance constraint between the obstacle and the ego vehicle."
                                    },
                                    "speed": {
                                        "type": "object",
                                        "properties": {
                                            "CompOp": {
                                                "type": "string",
                                                "enum": [">", "<", "==", "<=", ">="],
                                                "description": "Used to specify the type of constraint on the speed of the obstacle."
                                            },
                                            "speed_num": {
                                                "type": "number",
                                                "description": "Used to specify a specific speed value that should be generated appropriately, in km/h."
                                            }
                                        },
                                        "description": "An optional setting, used to constrain the obstacle's speed, in km/h."
                                    }
                                },
                                "description": "Used to describe obstacle information in the ego vehicle's driving environment, and can serve as part of the constraint conditions for rule triggering. It is important to note that 'find_obstacle' only considers the closest obstacle of the specified 'obstacle_type' in the specified 'position' relative to the ego vehicle."
                            },
                            "is_jam": {
                                "type": "boolean",
                                "description": "Used to specify whether the current driving environment is congested."
                            },
                            "find_signal": {
                                "type": "object",
                                "properties": {
                                    "signal_type": {
                                        "type": "string",
                                        "enum": ["yield_signal", "stop_signal", "speed_limit_signal", "no_parking_signal", "school_signal", "crosswalk_signal", "no_u-turn_signal", "no_honking_signal", "no_left_turn_signal"],
                                        "description": "Used to describe the types of traffic signals that may be encountered ahead."
                                    },
                                    "CompOp": {
                                        "type": "string",
                                        "enum": [">", "<", "==", "<=", ">="],
                                        "description": "Used to specify the type of constraint on the distance to the upcoming traffic signal."
                                    },
                                    "distance_num": {
                                        "type": "number",
                                        "description": "Used to specify a specific distance value that should be generated appropriately."
                                    }
                                },
                                "description": "This is mainly used in scenarios where traffic signal control may be encountered. Specifically, 'singal_type' defines the potential upcoming traffic signal type, and 'ComOp' along with 'distance' specifies the distance relation between the current vehicle position and the next traffic signal."
                            },
                            "find_traffic_light": {
                                "type": "object",
                                "properties": {
                                    "traffic_light_type": {
                                        "type": "string",
                                        "enum": ["left-turn_signal_light", "right-turn_signal_light", "straight-through_signal_light"],
                                        "description": "An optional setting, specifically used to indicate directional traffic lights, such as left-turn, straight-through, or right-turn signals. When the traffic light displays an arrow symbol, the corresponding 'traffic_light_type' should be set. If the traffic light is a standard circular light without any directional arrow, there is no need to set 'traffic_light_type'."
                                    },
                                    "color": {
                                        "type": "string",
                                        "enum": ["red", "green", "yellow", "black"],
                                        "description": "The color of the traffic light. It should be noted that 'black' indicates the presence of a traffic light with no active signal displayed."
                                    },
                                    "flash": {
                                        "type": "boolean",
                                        "description": "An optional setting, used to indicate whether the traffic light is flashing."
                                    },
                                    "CompOp": {
                                        "type": "string",
                                        "enum": [">", "<", "==", "<=", ">="],
                                        "description": "Used to specify the type of constraint on the distance to the upcoming traffic signal."
                                    },
                                    "distance_num": {
                                        "type": "number",
                                        "description": "Used to specify a specific distance value that should be generated appropriately."
                                    }
                                },
                                "description": "This primarily applies to scenarios where the vehicle may encounter traffic signal control. The focus here is on traffic lights that regulate the lane the vehicle is currently on. Specifically, 'traffic_light_type' defines the type of the upcoming traffic light, 'color' specifies its color, 'flash' indicates whether the light is flashing, and 'CompOp' together with 'distance' defines the spatial relationship between the vehicle's current position and the upcoming traffic signal."
                            },
                            "vehicle_state": {
                                "type": "object",
                                "properties": {
                                    "driving_state": {
                                        "type": "string",
                                        "enum": ["go_straight", "turn_left", "turn_right", "reverse", "change_lane_to_left", "change_lane_to_right", "turn_left_or_go_straight", "turn_right_or_go_straight", "u_turn", "towing", "turn_right_or_turn_left", "pull_over"],
                                        "description": "An optional setting, used to describe the ego vehicle's current primary driving mode."
                                    },
                                    "speed": {
                                        "type": "object",
                                        "properties": {
                                            "CompOp": {
                                                "type": "string",
                                                "enum": [">", "<", "==", "<=", ">="],
                                                "description": "Used to specify the type of constraint on the speed of the ego vehicle."
                                            },
                                            "speed_num": {
                                                "type": "number",
                                                "description": "Used to specify a specific speed value that should be generated appropriately, in km/h."
                                            }
                                        },
                                        "description": "An optional setting, used to constrain the ego vehicle's speed, in km/h."
                                    },
                                    "acceleration": {
                                        "type": "object",
                                        "properties": {
                                            "CompOp": {
                                                "type": "string",
                                                "enum": [">", "<", "==", "<=", ">="],
                                                "description": "Used to specify the type of constraint on the acceleration of the ego vehicle."
                                            },
                                            "acceleration_num": {
                                                "type": "number",
                                                "description": "Used to specify a specific acceleration value that should be generated appropriately, in m/s^2."
                                            }
                                        },
                                        "description": "An optional setting, used to constrain the ego vehicle's speed, in m/s^2."
                                    },
                                    "state": {
                                        "type": "string",
                                        "enum": ["left_turn_light", "right_turn_light", "fog_light", "low_beam", "high_beam", "hazard_warning_light", "position_light", "horn", "alternated_between_high_and_low_beams"],
                                        "description": "An optional setting, used to describe the lights and horn that are currently turned on in the vehicle."
                                    }
                                }
                            }
                        },
                        "description": "Mainly used to further refine the environmental constraints that must be satisfied when the rule takes effect. It should be noted that each constraint can appear multiple times, but they are combined with an 'and' relationship, so conflicts should be avoided."
                    },
                    "action": {
                        "type": "object",
                        "properties": {
                            "Whether_priority_change_lane": {
                                "type": "boolean",
                                "description": "Whether to prioritize changing lanes when lane change is possible."
                            },
                            "Whether_allow_u_turn": {
                                "type": "boolean",
                                "description": "Whether the ego vehicle is allowed to make a U-turn."
                            },
                            "Whether_allow_reverse": {
                                "type": "boolean",
                                "description": "Whether the ego vehicle is allowed to reverse."
                            },
                            "Forward_buffer_distance": {
                                "type": "integer",
                                "description": "Used to determine the distance, in meters, between the front of the vehicle and a obstacle ahead at which processing should begin."
                            },
                            "Backward_buffer_distance": {
                                "type": "integer",
                                "description": "Specifies the distance, in meters, between the rear of the ego vehicle and the obstacle after passing it, serving as the indicator that the obstacle has been fully processed."
                            },
                            "Lateral_buffer_distance": {
                                "type": "integer",
                                "description": "Used to specify the lateral buffer distance, in meters, between the ego vehicle and the obstacle during their interaction."
                            },
                            "Dynamic_Obstacle_Follow_distance": {
                                "type": "integer",
                                "description": "The minimum following distance when the ego vehicle is following a moving object."
                            },
                            "Dynamic_Obstacle_Overtake_distance": {
                                "type": "integer",
                                "description": "Used to specify the minimum yielding distance for the ego vehicle to vehicles/moving objects, excluding pedestrians/bicycles."
                            },
                            "Dynamic_Obstacle_Overtake_distance": {
                                "type": "integer",
                                "description": "Used to specify the buffer distance, in meters, that the ego vehicle must maintain when considering overtaking a moving obstacle ahead."
                            },
                            "Min_stop_distance": {
                                "type": "integer",
                                "description": "The minimum distance, in meters, that the ego vehicle must maintain from the obstacle after stopping, when the vehicle is required to stop due to the obstacle."
                            },
                            "Whether_declearation": {
                                "type": "boolean",
                                "description": "Used to specify whether the ego vehicle needs to slow down when encountering an obstacle."
                            },
                            "Static_Obstacle_Deceleration_ratio": {
                                "type": "number",
                                "description": "Used to specify the percentage by which the ego vehicle's speed should be reduced when encountering a static obstacle. This works in conjunction with 'Whether_declaration' and takes effect only when 'Whether_declaration' is set to True."
                            },
                            "Dynamic_Obstacle_Deceleration_ratio": {
                                "type": "number",
                                "description": "Used to specify the percentage by which the ego vehicle's speed should be reduced when encountering a moving obstacle. This works in conjunction with 'Whether_declaration' and takes effect only when 'Whether_declaration' is set to True."
                            },
                            "Min_speed_for_keep_clear":{
                                "type": "integer",
                                "description": "The expected minimum speed (km/h) of the vehicle when passing through a 'keep clear' zone."
                            },
                            "Whether_red_light_turn_right": {
                                "type": "boolean",
                                "description": "Used to specify whether the vehicle is allowed to proceed during a red light when turning right at an intersection controlled by a signal light."
                            },
                            "Time_interval_for_lane_change": {
                                "type": "integer",
                                "description": "Used to specify the minimum time interval between two consecutive lane changes, in seconds."
                            },
                            "Check_distance": {
                                "type": "integer",
                                "description": "Used to specify the length (in meters) of the forward area that requires special attention."
                            },
                            "Whether_allow_left_lane_change": {
                                "type": "boolean",
                                "description": "Specifies whether the ego vehicle is allowed to change to the left lane."
                            },
                            "Whether_allow_right_lane_change": {
                                "type": "boolean",
                                "description": "Specifies whether the ego vehicle is allowed to change to the right lane."
                            },
                            "Whether_allow_borrow_left_lane": {
                                "type": "boolean",
                                "description": "Whether the ego vehicle is permitted to temporarily borrow the lane on its left side."
                            },
                            "Whether_allow_borrow_right_lane": {
                                "type": "boolean",
                                "description": "Whether the ego vehicle is permitted to temporarily borrow the lane on its right side."
                            },
                            "Whether_allow_parking": {
                                "type": "boolean",
                                "description": "Whether the ego vehicle is allowed to park."
                            },
                            "Whether_check": {
                                "type": "object",
                                "properties": {
                                    "check_type": {
                                        'type': 'string',
                                        'enum': ['keep_clear', 'stop_signal', 'speed_limit_signal', 'yield_signal', 'crosswalk', 'traffic_light', 'intersection'],
                                        'description': 'Used to specify the traffic signals or road types.'
                                    },
                                    "check_sign": {
                                        "type": 'boolean',
                                        'description': "Used to specify whether monitoring is enabled: set to 'True' to enable monitoring, and 'False' to disable it."
                                    }
                                },
                                'description': "Used to indicate whether traffic signals or road types are being monitored. Specifically, 'check_type' specifies the object of interest, while 'check_sign' indicates whether it should be monitored."
                            },
                            "Preparation_distance": {
                                "type": "object",
                                "properties": {
                                    "reason": {
                                        'type': 'string',
                                        'enum': ['keep_clear', 'stop_signal', 'speed_limit_signal', 'yield_signal', 'crosswalk', 'traffic_light', 'destination', 'intersection'],
                                        'description': 'Used to specify the traffic signals or road types.'
                                    },
                                    "distance": {
                                        "type": "integer",
                                        "description": "Used to specify the distance (in meters) for advance preparation."
                                    }
                                },
                                "description": "Used to specify the preparation distance. When the distance between the vehicle and the traffic signal or road type defined in 'reason' reaches this value, the ego vehicle enters the preparation phase to respond accordingly."
                            },
                            "Stopping_distance": {
                                "type": "object",
                                "properties": {
                                    "reason": {
                                        'type': 'string',
                                        'enum': ['keep_clear', 'stop_signal', 'yield_signal', 'crosswalk', 'traffic_light', 'destination', 'intersection'],
                                        'description': 'Used to specify the traffic signals or road types.'
                                    },
                                    "distance": {
                                        "type": "integer",
                                        "description": "Used to specify the distance (in meters) between the vehicle and the stop line."
                                    }
                                },
                                "description": "Used to specify the distance the vehicle should maintain from the scenario defined in 'reason' when a stop is required before entering it."
                            },
                            "Wait_time": {
                                "type": "object",
                                "properties": {
                                    "reason": {
                                        'type': 'string',
                                        'enum': ['keep_clear', 'stop_signal', 'yield_signal', 'crosswalk', 'intersection'],
                                        'description': 'Used to specify the traffic signals or road types.'
                                    },
                                    "time": {
                                        "type": "integer",
                                        "description": "Used to specify the minimum waiting time after stopping, in seconds."
                                    }
                                },
                                "description": "Used to specify the minimum waiting time the vehicle should observe when a stop is required before entering the scenario defined in 'reason'."
                            },
                            "Creep_time": {
                                "type": "object",
                                "properties": {
                                    "reason": {
                                        'type': 'string',
                                        'enum': ['keep_clear', 'stop_signal', 'yield_signal', 'crosswalk', 'traffic_light', 'intersection'],
                                        'description': 'Used to specify the traffic signals or road types.'
                                    },
                                    "time": {
                                        "type": "integer",
                                        "description": "Used to specify the slow crawl duration after restarting from a stop, in seconds."
                                    }
                                },
                                "description": "Used to specify the slow crawl duration after restarting from a stop, in preparation for entering the scenario defined in 'reason'."
                            },
                            "Expected_speed": {
                                "type": "object",
                                "properties" : {
                                    "speed_number": {
                                        "type": "number",
                                        "description": "An optional setting, used to specify the desired driving speed, in km/h."
                                    },
                                    "limit_speed": {
                                        "type": "boolean",
                                        "description": "An optional setting, used to specify the speed required by the speed limit signal."
                                    }
                                },
                                "description": "Either 'speed_number' or 'limit_speed' can be used to specify the desired driving speed of the ego vehicle."
                            },
                            "Change_lane_action": {
                                "type": "object",
                                "properties": {
                                    "direction": {
                                        "type": "string",
                                        "enum": ["left", "right"],
                                        "description": "Used to specify the lane change direction of the ego vehicle, i.e., whether to change to the left or right lane."
                                    },
                                    "times": {
                                        "type": "integer",
                                        "description": "Used to specify the number of lane changes to be made."
                                    }
                                },
                                "description": "Instructs the ego vehicle to perform lane change operations in the direction specified by 'direction', for the number of times specified by 'times'."
                            },
                            "Mano_action": {
                                "type": "string",
                                "enum": ['borrow_lane', 'pull_over', 'stop', 'wait', 'launch', 'yield'],
                                "descriptiion": "Instructs the ego vehicle to perform corresponding actions: 'borrow_lane' indicates an attempt to borrow another lane, 'pull_over' instructs the vehicle to pull over, 'stop' indicates stopping in the middle of the road, 'wait' means to temporarily delay starting, and 'launch' instructs the vehicle to start moving."
                            },
                            "State_action": {
                                "type": "object",
                                "properties": {
                                    "target": {
                                        "type": "string",
                                        "enum": ["left_turn_light", "right_turn_light", "fog_light", "low_beam", "high_beam", "hazard_warning_light", "position_light", "horn", "alternated_between_high_and_low_beams"],
                                        "description": "Used to specify the target to be configured, including various vehicle lights and the horn."
                                    },
                                    "whether_turn_on": {
                                        "type": "boolean",
                                        "description": "Used to specify whether the device is turned on. Set to 'True' to turn on, and 'False' to turn off."
                                    }
                                },
                                "description": "Controls various lights and the horn of the ego vehicle. The device specified by 'target' is turned on or off based on the 'whether_turn_on' setting."
                            }
                        },
                        "description": "Specifies the operation the vehicle is required to perform in the environment defined by 'trigger' and 'condition'."
                    },
                }
            }
        }
    }
    return [UDrive]

def creat_ENBF():
    with open("Grammer.txt", "r") as f:
        grammar = f.read()
    f.close()
    return grammar    

def talk_with_LLM(model, client, messages, tools = None):
    if tools != None:
        params = {
            'model': model,
            'messages': messages,
            'tools': tools
        }
    else:
        params = {
            'model': model,
            'messages': messages
        }

    response = client.chat.completions.create(**params)
    return response.choices[0].message

def get_spec(spec_name):
    with open(spec_name) as f:
        spec = json.load(f)
    f.close()
    return spec

def get_example(example_name, spec, method, number = 4):
    if method == "Function":
        part = ["Original expression", "Thought process", "Function call"]
    elif method == "EBNF":
        part = ["Original expression", "Thought process", "Result"]
    elif method == "GP":
        part = ["Original expression", "Grammar", "Result"]
    with open(example_name) as f:
        example = json.load(f)
    f.close()
    sample_items = random.sample(list(example.items()), number)
    example_ = dict(sample_items)
    example = []
    for _, v in example_.items():
        example_part = ''
        for i in part:
            example_part += i + ': ' + v[i]
        if example_part != '':
            example.append(example_part)
    spec_filter = {k : v for k, v in spec.items() if k not in example_}
    if method == "GP":
        return example_, spec_filter 
    return example, spec_filter

def Talk_main(client, model, spec_name, example_name, record_name, method, fail_name):
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    fail_name = record_name + "/" + now_str + "_" + method + "_fail.txt"
    record_name = record_name + "/" + now_str + "_" + method + ".txt"
    if os.path.exists(record_name): open(record_name, 'w').close()
    if os.path.exists(fail_name): open(fail_name, 'w').close()
    specs = get_spec(spec_name)
    example, specs = get_example(example_name, specs, method)
    if method == "Function":
        tools = create_function_list()
        for key, spec in tqdm(specs.items(), desc="Processing"):
            # if key != "9":
            #     continue
            print(f"Currently processing: {key}")
            message = [{"role": "user", "content": "You are a professional programmer with expertise in vehicle driving scenarios. Based on the provided natural language description, generate some appropriate function calls. For descriptions that are not related to automobile driving, no function call should be generated. If the constraints cannot capture the scenario accurately or if no corresponding action exists, do not fabricate commands."}]
            message.append({"role": "user", "content": "Here is some example:"})
            for i in example:
                message.append({"role": "user", "content": i})
            message.append({"role": "user", "content": spec})
            message.append({"role": "user", "content": "The returned result does not need explanation."})
            try:
                result = talk_with_LLM(model, client, message, tools)
            except Exception as e:
                with open(fail_name, 'a') as f:
                    f.write(key + ": " + spec + "\n")
                    f.write(str(e)+ "\n\n")
                continue
            with open(record_name, 'a') as f:
                f.write(key + ": " + spec + "\n")
                try:
                    for item in result.tool_calls:
                        f.write(str(item.function) + '\n')
                    f.write('\n')
                except Exception as e:
                    continue 
    elif method == "EBNF":
        grammar = creat_ENBF()
        for key, spec in tqdm(specs.items(), desc="Processing"):
            print(f"Currently processing: {key}")
            message = [{"role": "user", "content": "You are an expert programmer, and you need to write a program for the given natural language query. First, you should write a grammar that contains all the necessary EBNF rules. Then, you should write programs that conform to your predicted rules."}]
            message.append({"role": "user", "content": "The following is the syntax definition of my custom DSL language (written in EBNF):" + grammar})
            for i in example:
                message.append({"role": "user", "content": i})
            message.append({"role": "user", "content": spec})
            message.append({"role": "user", "content": "The returned result does not need explanation."})
            try:
                result = talk_with_LLM(model, client, message)
            except Exception as e:
                with open(fail_name, 'a') as f:
                    f.write(key + ": " + spec + "\n")
                    f.write(str(e)+ "\n\n")
                continue
            with open(record_name, 'a') as f:
                f.write(key + ": " + spec + "\n")
                f.write(str(result.content) + '\n\n')
    elif method == "GP":
        DELIMITER = "\nprogram based on the EBNF grammar rules:\n"
        prompt = {
            "instruction" : ("You are an expert programmer, and you need to write a program" 
                        " for the given natural language query.\n"),
            "rule_instruction" : "",
            "exampler" : lambda ex: f"query: {ex["Original expression"]}\nBNF grammar rules:\n{ex["Grammar"]}{DELIMITER}{ex["Result"]}\n\n",
            "rule_exampler" : lambda ex: f"query: {ex.source}\nBNF grammar rules:\n{ex.grammar}\n\n",
            "prediction": lambda ex: f"query: {ex}\nBNF grammar rules:\n",
            "prediction_given_rule": lambda ex: f"query: {ex.source}\nBNF grammar rules:\n{ex.grammar}{DELIMITER}"
        }
        instruction = "First, you should write grammar rules by choosing from the following EBNF rules. Then, you should write programs that conform to your predicted rules.\n"
        with open("Grammer.txt", "r") as f:
            grammar = f.read()
        f.close()
        instruction = f"{instruction}\n[BEGIN RULES]\n{grammar}\n[END RULES]\n\n"
        prompt["rule_instruction"] = instruction
        for key, spec in tqdm(specs.items(), desc="Processing"):
            print(f"Currently processing: {key}")
            one_show_prompt = prompt["instruction"]
            one_show_prompt += prompt["rule_instruction"]
            for _, spec1 in example.items():
                one_show_prompt += prompt["exampler"](spec1)
            one_show_prompt += prompt["prediction"](spec)
            try:
                result = talk_with_LLM(model, client, [{"role":"user", "content" : one_show_prompt}])
            except Exception as e:
                with open(fail_name, 'a') as f:
                    f.write(key + ": " + spec + "\n")
                    f.write(str(e)+ "\n\n")
                continue
            with open(record_name, 'a') as f:
                f.write(key + ": " + spec + "\n")
                f.write(str(result.content) + '\n\n')

if __name__ == "__main__":
    # client = OpenAI(api_key = "", base_url = "")
    client = OpenAI(api_key="")
    model =  "gpt-4.1"     #['deepseek-reasoner', "deepseek-chat","gpt-4.1", "o4-mini-2025-04-16", "gpt-4o-2024-08-06"]
    spec_name = ""
    example_name = ""
    record_name = "Records/China_spec/"
    method = ""  #["EBNF", "Function"， "GP"]
    Talk_main(client, model, spec_name, example_name, record_name, method)