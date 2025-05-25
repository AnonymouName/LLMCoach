import json, re, os
from openai import OpenAI
from collections import deque

RoadTypeValue = ["urban_lane", "intersection", "bridge", "ferry_crossing", "mountain_road", "icy_road", "flooded_road", "flooded_bridge", "motorway", "railway_crossing", "sharp_curve", "narrow_road", "narrow_bridge", "muddy_road", "non-motorized", "steep_slope", "sharp_bend", "roundabout", "crosswalk", "no_parking_zone", "tunnel", "highway", "highway_exit_ramp"]
TimeValue = ["daytime", "night"]
WeatherValue = ["raining", "foggy", "snowing", "sandstorm", "hail"]
SpecialLaneValue = ["fast_lane", "bus_lane", "emergency_lane", "without_centerline", "one_lane_same_direction", "non_motorized"]
CompOpValue = [">", "<", "==", "<=", ">="]
ObstacleValue = ["all", "vehicle", "pedestrian", "bicycle", "motorcycle", "non-motorized", "others"]
PositionValue = ["left", "right", "front", "back"]
DirectionValue = ["same", "opposite"]
SignalTypeValue = ["traffic_light", "yield_signal", "stop_signal", "speed_limit_signal", "no_parking_signal", "school_signal", "crosswalk_signal", "no_u-turn_signal", "no_honking_signal", "no_left_turn_signal"]
TrafficLightTypeValue = ["motor_vehicle_signal_light", "left-turn_signal_light", "right-turn_signal_light", "straight-through_signal_light", "warning_signal_light"]
ColorValue = ["red", "green", "yellow", "black"]
DrivingStateValue = ["go_straight", "turn_left", "turn_right", "reverse", "change_lane_to_left", "change_lane_to_right", "turn_left_or_go_straight", "turn_right_or_go_straight", "u_turn", "towing", "turn_left_or_turn_right", "pull_over"]
StateValue = ["left_turn_light", "right_turn_light", "fog_light", "low_beam", "high_beam", "hazard_warning_light", "position_light", "horn", "alternated_between_high_and_low_beams"]
ManoValue = ['borrow_lane', 'pull_over', 'stop', 'wait', 'launch', 'yield']

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

def parse(result):
    try:
        arguments = json.loads(result)
    except:
        return False, "Error: Parsing failed - the function call is not a valid function call format."
    for key1, value1 in arguments.items():
        if key1 == "trigger":
            if len(value1) > 1:
                return False, "Error: Trigger parsing failed — multiple properties detected in a single trigger, which is not allowed."
            for key2, value2 in value1.items():
                if key2 == "always":
                    if not isinstance(value2, bool): return False, "Error: Trigger parsing failed - the value assigned to 'always' is not a boolean."
                elif key2 in ['in', 'not_in']:
                    if str(value2) not in RoadTypeValue: return False, "Error: Trigger parsing failed - the value assigned to '" + key2 + "' is not a valid value."
                else:
                    return False, "Error: Trigger parsing failed - '" + key2 + "' is an invalid property in trigger."                
        elif key1 == "condition":
            if value2 == {}:
                continue
            for key2, value2 in value1.items():
                if key2 == "time_is":
                    if value2 not in TimeValue: return False, "Error: Condition parsing failed - the value assigned to '" + key2 + "' is not a valid value."
                elif key2 == "weather_is":
                    if value2 not in WeatherValue: return False, "Error: Condition parsing failed - the value assigned to '" + key2 + "' is not a valid value."
                elif key2 in ["is_special_lane", "not_special_lane"]:
                    if value2 not in SpecialLaneValue: return False, "Error: Condition parsing failed - the value assigned to '" + key2 + "' is not a valid value."
                elif key2 == "distance_to":
                    if len(value2) != 3: return False, "Error: Condition parsing failed - the required property of '" + key2 + "' is missing."
                    for key3, value3 in value2.items():
                        if key3 == "road_type" and value3 not in RoadTypeValue: return False, "Error: Condition parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                        elif key3 == "CompOp" and value3 not in CompOpValue: return False, "Error: Condition parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                        elif key3 == "distance_num" and not isinstance(value3, (int, float)): return False, "Error: Condition parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                        elif key3 not in ["road_type", "CompOp", "distance_num"]: return False, "Error: Condition parsing failed - '" + key3 + "' is an invalid property in '" + key2 + "'."
                elif key2 == "find_obstacle":
                    if "obstacle_type" not in value2.keys() or "position" not in value2.keys() or "distance" not in value2.keys(): return False, "Error: Condition parsing failed - the required property of '" + key2 + "' is missing."
                    for key3, value3 in value2.items():
                        if key3 == "obstacle_type" and value3 not in ObstacleValue: return False, "Error: Condition parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                        elif key3 == "position" and value3 not in PositionValue: return False, "Error: Condition parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                        elif key3 == "direction" and value3 not in DirectionValue: return False, "Error: Condition parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                        elif key3 == "distance":
                            if len(value3) != 2: return False, "Error: Condition parsing failed - the required property of '" + key3 + "' in '" + key2 + "' is missing."
                            for key4, value4 in value3.items():
                                if key4 == "CompOp" and value4 not in CompOpValue: return False, "Error: Condition parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                                elif key4 == "distance_num" and not isinstance(value4, (int, float)): return False, "Error: Condition parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                                elif key4 not in ["CompOp", "distance_num"]: return False, "Error: Condition parsing failed - '" + key4 + "' is an invalid property of '" + key3 + "' in '" + key2 +"'."
                        elif key3 == "speed":
                            if len(value3) != 2: return False, "Error: Condition parsing failed - the required property of '" + key3 + "' in '" + key2 + "' is missing."
                            for key4, value4 in value3.items():
                                if key4 == "CompOp" and value4 not in CompOpValue: return False, "Error: Condition parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                                elif key4 == "speed_num" and not isinstance(value4, (int, float)): return False, "Error: Condition parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                                elif key4 not in ["CompOp", "speed_num"]: return False, "Error: Condition parsing failed - '" + key4 + "' is an invalid property of '" + key3 + "' in '" + key2 +"'."
                        elif key3 not in ["obstacle_type", "position", "direction", "distance", "speed"]: return False, "Error: Condition parsing failed - '" + key3 + "' is an invalid property in '" + key2 + "'."
                elif key2 == "is_jam":
                    if not isinstance(value2, bool): return False, "Error: Condition parsing failed - the value assigned to '" + key2 + "' is not a valid value."
                elif key2 == "find_signal":
                    if len(value2) != 3: return False, "Error: Condition parsing failed - the required property of '" + key2 + "' is missing."
                    for key3, value3 in value2.items():
                        if key3 == "signal_type" and value3 not in SignalTypeValue: return False, "Error: Condition parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                        elif key3 == "CompOp" and value3 not in CompOpValue: return False, "Error: Condition parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                        elif key3 == "distance_num" and not isinstance(value3, (int, float)): return False, "Error: Condition parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                        elif key3 not in ["signal_type", "CompOp", "distance_num"]: return False, "Error: Condition parsing failed - '" + key3 + "' is an invalid property in '" + key2 + "'."
                elif key2 == "find_traffic_light":
                    if "color" not in value2.keys() or "CompOp" not in value2.keys() or "distance_num" not in value2.keys(): return False, "Error: Condition parsing failed - the required property of '" + key2 + "' is missing."
                    for key3, value3 in value2.items():
                        if key3 == "traffic_light_type" and value3 not in TrafficLightTypeValue: return False, "Error: Condition parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                        elif key3 == "color" and value3 not in ColorValue: return False, "Error: Condition parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                        elif key3 == "flash" and not isinstance(value3, bool): return False, "Error: Condition parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                        elif key3 == "CompOp" and value3 not in CompOpValue: return False, "Error: Condition parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                        elif key3 == "distance_num" and not isinstance(value3, (int, float)): return False, "Error: Condition parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                        elif key3 not in ["traffic_light_type", "color", "flash", "CompOp", "distance_num"]: return False, "Error: Condition parsing failed - '" + key3 + "' is an invalid property in '" + key2 + "'."
                elif key2 == "vehicle_state":
                    for key3, value3 in value2.items():
                        if key3 == "driving_state" and value3 not in DrivingStateValue: return False, "Error: Condition parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                        elif key3 == "speed":
                            if len(value2) != 2: return False, "Error: Condition parsing failed - the required property of '" + key3 + "' in '" + key2 + "' is missing."
                            for key4, value4 in value3.items():
                                if key4 == "CompOp" and value4 not in CompOpValue: return False, "Error: Condition parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                                elif key4 == "speed_num" and not isinstance(value4, (int, float)): return False, "Error: Condition parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                                elif key4 not in ["CompOp", "speed_num"]: return False, "Error: Condition parsing failed - '" + key4 + "' is an invalid property of '" + key3 + "' in '" + key2 +"'."
                        elif key3 == "acceleration":
                            if len(value2) != 2: return False, "Error: Condition parsing failed - the required property of '" + key3 + "' in '" + key2 + "' is missing."
                            for key4, value4 in value3.items():
                                if key4 == "CompOp" and value4 not in CompOpValue: return False, "Error: Condition parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                                elif key4 == "acceleration_num" and not isinstance(value4, (int, float)): return False, "Error: Condition parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                                elif key4 not in ["CompOp", "acceleration_num"]: return False, "Error: Condition parsing failed - '" + key4 + "' is an invalid property of '" + key3 + "' in '" + key2 +"'."
                        elif key3 == "state" and value3 not in StateValue: return False, "Error: Condition parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                        elif key3 not in ["driving_state", "speed", "acceleration", "state"]: return False, "Error: Condition parsing failed - '" + key3 + "' is an invalid property in '" + key2 + "'."
                else:
                    return False, "Error: Condition parsing failed - '" + key2 + "' is an invalid property in condition."
        elif key1 == "action":
            for key2, value2 in value1.items():
                if key2 in ["Whether_priority_change_lane", "Whether_allow_borrow_lane", "Whether_allow_u_turn", "Whether_allow_reverse", "Whether_declearation", "Whether_red_light_turn_right", "Whether_allow_left_lane_change", "Whether_allow_right_lane_change"]:
                    if not isinstance(value2, bool): return False, "Error: Action parsing failed - the value assigned to '" + key2 + "' is not a valid value."
                elif key2 in ["Forward_buffer_distance", "Backward_buffer_distance", "Lateral_buffer_distance", "Dynamic_Obstacle_Follow_distance", "Dynamic_Obstacle_Overtake_distance", "Dynamic_Obstacle_Overtake_distance", "Min_stop_distance", "Static_Obstacle_Deceleration_ratio", "Dynamic_Obstacle_Deceleration_ratio", "Min_speed_for_keep_clear", "Time_interval_for_lane_change", "Check_distance"]:
                    if not isinstance(value2, (int, float)): return False, "Error: Action parsing failed - the value assigned to '" + key2 + "' is not a valid value."
                elif key2 == "Whether_check":
                    if len(value2) != 2: return False, "Error: Action parsing failed - the required property of '" + key2 + "' is missing."
                    for key3, value3 in value2.items():
                        if key3 == "check_type" and value3 not in RoadTypeValue and value3 not in TrafficLightTypeValue: return False, "Error: Action parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                        elif key3 == "check_sign" and not isinstance(value3, bool): return False, "Error: Action parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                        elif key3 not in ["check_type", "check_sign"]: return False, "Error: Condition parsing failed - '" + key3 + "' is an invalid property in '" + key2 + "'."
                elif key2 in ["Preparation_distance", "Stopping_distance"]:
                    if len(value2) != 2: return False, "Error: Action parsing failed - the required property of '" + key2 + "' is missing."
                    for key3, value3 in value2.items():
                        if key3 == "reason" and value3 not in RoadTypeValue and value3 not in TrafficLightTypeValue: return False, "Error: Action parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                        elif key3 == "distance" and not isinstance(value3, (int, float)): return False, "Error: Action parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                        elif key3 not in ["reason", "distance"]: return False, "Error: Condition parsing failed - '" + key3 + "' is an invalid property in '" + key2 + "'."
                elif key2 in ["Wait_time", "Creep_time"]:
                    if len(value2) != 2: return False, "Error: Action parsing failed - the required property of '" + key2 + "' is missing."
                    for key3, value3 in value2.items():
                        if key3 == "reason" and value3 not in RoadTypeValue and value3 not in TrafficLightTypeValue: return False, "Error: Action parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                        elif key3 == "time" and not isinstance(value3, (int, float)): return False, "Error: Action parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                        elif key3 not in ["reason", "time"]: return False, "Error: Condition parsing failed - '" + key3 + "' is an invalid property in '" + key2 + "'."
                elif key2 == "Expected_speed":
                    for key3, value3 in value2.items():
                        if key3 == "limit_speed" and not isinstance(value3, bool): return False, "Error: Action parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                        elif key3 == "speed_number" and not isinstance(value3, (int, float)): return False, "Error: Action parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                        elif key3 not in ["limit_speed", "speed_number"]: return False, "Error: Action parsing failed - '" + key3 + "' is an invalid property in '" + key2 + "'."
                elif key2 == "Change_lane_action":
                    if len(value2) != 2: return False, "Error: Action parsing failed - the required property of '" + key2 + "' is missing."
                    for key3, value3 in value2.items():
                        if key3 == "direction" and value3 not in ["left", "right"]: return False, "Error: Action parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                        elif key3 == "times" and not isinstance(value3, (int, float)): return False, "Error: Action parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                        elif key3 not in ["direction", "times"]: return False, "Error: Condition parsing failed - '" + key3 + "' is an invalid property in '" + key2 + "'."
                elif key2 == "Mano_action":
                    if value2 not in ManoValue: return False, "Error: Action parsing failed - the value assigned to '" + key2 + "' is not a valid value."
                elif key2 == "State_action":
                    if len(value2) != 2: return False, "Error: Action parsing failed - the required property of '" + key2 + "' is missing."
                    for key3, value3 in value2.items():
                        if key3 == "target" and value3 not in StateValue: return False, "Error: Action parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                        elif key3 == "whether_turn_on" and not isinstance(value3, bool): return False, "Error: Action parsing failed - the value assigned to '" + key3 + "' in '" + key2 + "' is not a valid value."
                        elif key3 not in ["target", "whether_turn_on"]: return False, "Error: Condition parsing failed - '" + key3 + "' is an invalid property in '" + key2 + "'."
                else:
                    return False, "Error: Action parsing failed - '" + key2 + "' is an invalid property in action."
        else:
            return False, "Error: UDrive parsing failed - '" + key1 + "' is an invalid property in UDrive."
    return True, ''

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

def get_example(example_name):
    part = ["Original expression", "Thought process", "Function call"]
    with open(example_name) as f:
        example_ = json.load(f)
    f.close()
    example = []
    for _, v in example_.items():
        example_part = ''
        for i in part:
            example_part += i + ': ' + v[i]
        if example_part != '':
            example.append(example_part)
    return example

def Parse_based_dealwith(model, client, record_name, example_name):
    new_file = record_name.split('.')[0] + "_parse.txt"
    if os.path.exists(new_file): open(new_file, 'w').close()
    example = get_example(example_name)
    tools = create_function_list()
    with open(record_name, "r") as f:
        lines = f.readlines()
    
    line_index = 0
    description = []
    calls = deque()
    while line_index < len(lines):
        description = lines[line_index].split(': ')
        line_index += 1
        with open(new_file, 'a') as f:
            f.write(f"{description[0]}: {': '.join(description[1:])}")
            while lines[line_index] != "\n":
                calls.append(lines[line_index])
                line_index += 1
            
            while calls:
                call = calls.popleft()
                related = re.search(r"arguments='(.*?)'", call)
                parse_result, detailed = parse(related.group(1))
                times = 0
                if parse_result:
                        f.write(call)
                else:
                    message = [{"role": "user", "content": "You are an expert programmer, and you need to write a program for the given natural language query. It should be noted that if the constraints cannot express the user's described scenario or if there is no corresponding action, do not generate commands arbitrarily."}]
                    message.append({"role": "user", "content": "Here is some example:"})
                    for i in example:
                        message.append({"role": "user", "content": i})
                    message.append({"role": "user", "content": "The previously provided rule was: " + ': '.join(description[1:])})
                    message.append({"role": "user", "content": "The function call you provided for this is: " + call})
                    message.append({"role": "user", "content": "However, an error occurred during the parsing process. The specific error message is: " + detailed})
                    message.append({"role": "user", "content": "Please regenerate correct function calls and include them in the tools_call section of the response."})

                    new_result= []
                    while times < 5:
                        try:
                            flag = True
                            talk_result = talk_with_LLM(model, client, message, tools)
                            for item in talk_result.tool_calls:
                                new_parse_reslut, _= parse(str(item.function.arguments))
                                if not new_parse_reslut:
                                    flag = False
                            if flag:
                                for item in talk_result.tool_calls:
                                    item = str(item.function)
                                    if item not in new_result:
                                        new_result.append(item)
                        except:
                            continue
                        times += 1
                    if new_result:
                        for item in new_result:
                            f.write(item + "\n")
                    else:
                        f.write("Error: Unable to generate a valid function call. Please check the input and try again.\n")
            f.write("\n")                                                    
        line_index += 1


if __name__ == "__main__":
    client = OpenAI(api_key = "", base_url = "")
    model =  ""     #['deepseek-reasoner', "deepseek-chat","gpt-4.1", "o4-mini-2025-04-16", "gpt-4o-2024-08-06"]
    record_name = ""
    example_name = "Specs/China_spec_example.json"
    Parse_based_dealwith(model, client, record_name, example_name)
   