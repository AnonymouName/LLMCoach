import re

def split_calls(calls, batch_size):
    return [calls[i:i + batch_size] for i in range(0, len(calls), batch_size)]

def deal_with_initial_generation(record_name):
    with open(record_name, "r") as f:
        lines = f.readlines()
    calls = []

    for line in lines:
        related = re.search(r"arguments='(.*?)'", line)
        if related:
            calls.append(related.group(1))
    return calls

def extract_fuzzy_function_blocks(name):
    with open(name, "r", encoding="utf-8") as f:
        text = f.read()

    text = text.replace('\\"', '"')  # 合理转义处理

    blocks = []
    buffer = ""
    stack = []

    i = 0
    while i < len(text):
        ch = text[i]

        # 检测“触发新 trigger 但旧块未闭合”时的容错
        lookahead = text[i:i+15].lower()
        if '"trigger"' in lookahead and stack and len(stack) > 3:
            # 前一块可能崩了，丢弃它
            buffer = ""
            stack = []

        if ch == "{":
            if not stack:
                buffer = ""  # 新块开始
            stack.append("{")

        if stack:
            buffer += ch

        if ch == "}":
            if stack:
                stack.pop()
            if not stack:
                # 只记录含 trigger 和 action 的块
                if "trigger" in buffer and "action" in buffer:
                    blocks.append(buffer.strip())
                buffer = ""

        i += 1

    return blocks



def extract_fuzzy_function_blocks_s(name):
    with open(name, "r") as f:
        text = f.read()
    # 处理转义字符
    text = text.replace('\\"', '"').replace('\\', '')
    # 提取所有的 {...} 块
    blocks = []
    buffer = ""
    stack = []

    for i, ch in enumerate(text):
        if ch == "{":
            if not stack:
                buffer = ""  # 开始新块
            stack.append("{")
        if stack:
            buffer += ch
        if ch == "}":
            stack.pop()
            if not stack:
                # 一个完整的 {...} 出现了
                if "trigger" in buffer and "action" in buffer:
                    blocks.append(buffer.strip())
        

    return blocks

def extract_dsl_from_raw_string(raw_str):
    raw_str = raw_str.replace('\\"', '"').replace('\\', '')

    trigger_dsl = ""
    condition_dsl = ""
    action_dsl = ""

    # ------- trigger -------
    trigger_block = re.search(r'"trigger"\s*:\s*{(.*?)}', raw_str, re.DOTALL)
    if trigger_block:
        tb = trigger_block.group(1)
        if '"always"' in tb:
            trigger_dsl = "always"
        elif '"in"' in tb:
            val = re.search(r'"in"\s*:\s*"([^"]+)"', tb)
            if val:
                trigger_dsl = f'in({val.group(1)})'
        elif '"not_in"' in tb:
            val = re.search(r'"not_in"\s*:\s*"([^"]+)"', tb)
            if val:
                trigger_dsl = f'not_in({val.group(1)})'

    # ------- condition -------
    condition_block = re.search(r'"condition"\s*:\s*{(.*?)}\s*,?\s*"action"', raw_str, re.DOTALL)
    condition_clauses = []
    if condition_block:
        cb = condition_block.group(1)
        # find_signal
        fsig_blocks = re.findall(r'"find_signal"\s*:\s*{(.*?)}', cb, re.DOTALL)
        for block in fsig_blocks:
            sig_type = re.search(r'"signal_type"\s*:\s*"([^"]+)"', block)
            comp = re.search(r'"CompOp"\s*:\s*"([^"]+)"', block)
            dist = re.search(r'"distance_num"\s*:\s*(\d+)', block)
            if sig_type and comp and dist:
                condition_clauses.append(f'find_signal({sig_type.group(1)}, {comp.group(1)}, {dist.group(1)})')

        # weather_is
        weathers = re.findall(r'"weather_is"\s*:\s*"([^"]+)"', cb)
        for weather in weathers:
            condition_clauses.append(f'weather_is({weather})')

        # time_is
        times = re.findall(r'"time_is"\s*:\s*"([^"]+)"', cb)
        for time in times:
            condition_clauses.append(f'time_is({time})')

        # is_jam
        is_jams = re.findall(r'"is_jam"\s*:\s*(true|false)', cb, re.IGNORECASE)
        for is_jam in is_jams:
            condition_clauses.append('is_jam' if is_jam.lower() == 'true' else '!is_jam')

        # is_special_lane
        is_special_lanes = re.findall(r'"is_special_lane"\s*:\s*"([^"]+)"', cb)
        for is_special_lane in is_special_lanes:
            condition_clauses.append(f'is_special_lane({is_special_lane})')

        # not_special_lane
        not_special_lanes = re.findall(r'"not_special_lane"\s*:\s*"([^"]+)"', cb)
        for not_special_lane in not_special_lanes:
            condition_clauses.append(f'!is_special_lane({not_special_lane})')

        # distance_to
        distance_blocks = re.findall(r'"distance_to"\s*:\s*{(.*?)}', cb, re.DOTALL)
        for block in distance_blocks:
            road_type = re.search(r'"road_type"\s*:\s*"([^"]+)"', block)
            comp_op = re.search(r'"CompOp"\s*:\s*"([^"]+)"', block)
            distance = re.search(r'"distance_num"\s*:\s*(\d+)', block)
            if road_type and comp_op and distance:
                condition_clauses.append(f'distance_to({road_type.group(1)}, {comp_op.group(1)}, {distance.group(1)})')
        
        # find_obstacle
        fods = re.findall(r'"find_obstacle"\s*:\s*{(.*?)}\s*(?:,|$)', cb, re.DOTALL)
        for obstacle_block in fods:
            obstacle_type = re.search(r'"obstacle_type"\s*:\s*"([^"]+)"', obstacle_block)
            position = re.search(r'"position"\s*:\s*"([^"]+)"', obstacle_block)
            direction = re.search(r'"direction"\s*:\s*"([^"]+)"', obstacle_block)
            dist = re.search(r'"distance"\s*:\s*{[^}]*"CompOp"\s*:\s*"([<>=!]+)"[^}]*"distance_num"\s*:\s*(\d+)', obstacle_block)
            speed = re.search(r'"speed"\s*:\s*{[^}]*"CompOp"\s*:\s*"([<>=!]+)"[^}]*"speed_num"\s*:\s*(\d+)', obstacle_block)
            parts = []
            if obstacle_type: parts.append(obstacle_type.group(1))
            if position: parts.append(position.group(1))
            if direction: parts.append(direction.group(1))
            if dist: parts.append(f'({dist.group(1)}, {dist.group(2)}m)')
            if speed: parts.append(f'({speed.group(1)}, {speed.group(2)}km/h)')
            if parts: condition_clauses.append(f'find_obstacle({", ".join(parts)})')

        # find_traffic_light
        ftls = re.findall(r'"find_traffic_light"\s*:\s*{(.*?)}\s*(?:,|$)', cb, re.DOTALL)
        for traffic_light_block in ftls:
            color = re.search(r'"color"\s*:\s*"([^"]+)"', traffic_light_block)
            tl_type = re.search(r'"traffic_light_type"\s*:\s*"([^"]+)"', traffic_light_block)
            comp_op = re.search(r'"CompOp"\s*:\s*"([<>=!]+)"', traffic_light_block)
            dist = re.search(r'"distance_num"\s*:\s*(\d+)', traffic_light_block)
            parts = []
            if tl_type: parts.append(tl_type.group(1))
            if color: parts.append(color.group(1))
            if comp_op: parts.append(comp_op.group(1))
            if dist: parts.append(f'({dist.group(1)}m)')
            if parts: condition_clauses.append(f'find_traffic_light({", ".join(parts)})')


        # vehicle_state
        vss = re.findall(r'"vehicle_state"\s*:\s*{(.*?)}', cb, re.DOTALL)
        for vs_block in vss:
            driving_state = re.search(r'"driving_state"\s*:\s*"([^"]+)"', vs_block)
            speed = re.search(r'"speed"\s*:\s*{[^}]*"CompOp"\s*:\s*"([<>=!]+)"[^}]*"speed_num"\s*:\s*(\d+)', vs_block)
            accel = re.search(r'"acceleration"\s*:\s*{[^}]*"CompOp"\s*:\s*"([<>=!]+)"[^}]*"acceleration_num"\s*:\s*(\d+)', vs_block)
            state = re.search(r'"state"\s*:\s*"([^"]+)"', vs_block)
            parts = []
            if driving_state: parts.append(driving_state.group(1))
            if speed: parts.append(f'({speed.group(1)}, {speed.group(2)}km/h)')
            if accel: parts.append(f'({accel.group(1)}, {accel.group(2)}m/s²)')
            if state: parts.append(state.group(1))
            if parts: condition_clauses.append(f'vehicle_state({", ".join(parts)})')

    if condition_clauses:
        condition_dsl = '\n    '.join(condition_clauses)

    # ------- action -------
    action_match = re.search(r'"action"\s*:\s*(\{.*?\}|\[.*?\])\s*[,}]', raw_str, re.DOTALL)
    if action_match:
        actions = []
        action_raw = action_match.group(1).strip()

        def parse_action_dict(action_str):
            local_actions = []

            Mano_actions = re.findall(r'"Mano_action"\s*:\s*"([^"]+)"', action_str)
            for action in Mano_actions:
                local_actions.append(f'Mano({action})')

            if '"State_action"' in action_str:
                targets = re.findall(r'"target"\s*:\s*"([^"]+)"', action_str)
                states = re.findall(r'"whether_turn_on"\s*:\s*(true|false)', action_str, re.IGNORECASE)
                local_actions.extend(
                    f'State({t},{s.capitalize()})' for t, s in zip(targets, states)
                )
            
            whether_checks = re.findall(r'"Whether_check"\s*:\s*{(.*?)}', action_str, re.DOTALL)
            for block in whether_checks:
                check_type = re.search(r'"check_type"\s*:\s*"([^"]+)"', block)
                check_sign = re.search(r'"check_sign"\s*:\s*(true|false)', block, re.IGNORECASE)
                if check_type and check_sign:
                    local_actions.append(
                        f'Set(Whether_check, {check_type.group(1)}, {check_sign.group(1).capitalize()})'
                    )
            
            preparation_blocks = re.findall(r'"Preparation_distance"\s*:\s*{(.*?)}', action_str, re.DOTALL)
            for block in preparation_blocks:
                reason = re.search(r'"reason"\s*:\s*"([^"]+)"', block)
                distance_num = re.search(r'"distance"\s*:\s*(\d+)', block)
                if reason and distance_num:
                    local_actions.append(f'Set(Preparation_distance, {reason.group(1)}, {distance_num.group(1)})')

            
            stopping_blocks = re.findall(r'"Stopping_distance"\s*:\s*{(.*?)}', action_str, re.DOTALL)
            for block in stopping_blocks:
                reason = re.search(r'"reason"\s*:\s*"([^"]+)"', block)
                distance_num = re.search(r'"distance"\s*:\s*(\d+)', block)
                if reason and distance_num:
                    local_actions.append(f'Set(Stopping_distance, {reason.group(1)}, {distance_num.group(1)})')

            
            wait_time_blocks = re.findall(r'"Wait_time"\s*:\s*{(.*?)}', action_str, re.DOTALL)
            for block in wait_time_blocks:
                reason = re.search(r'"reason"\s*:\s*"([^"]+)"', block)
                time_num = re.search(r'"time"\s*:\s*(\d+)', block)
                if reason and time_num:
                    local_actions.append(f'Set(Wait_time, {reason.group(1)}, {time_num.group(1)}s)')


            creep_time_blocks = re.findall(r'"Creep_time"\s*:\s*{(.*?)}', action_str, re.DOTALL)
            for block in creep_time_blocks:
                reason = re.search(r'"reason"\s*:\s*"([^"]+)"', block)
                time_num = re.search(r'"time"\s*:\s*(\d+)', block)
                if reason and time_num:
                    local_actions.append(f'Set(Creep_time, {reason.group(1)}, {time_num.group(1)}s)')


            expected_speeds = re.findall(r'"Expected_speed"\s*:\s*{(.*?)}', action_str, re.DOTALL)
            for block in expected_speeds:
                speed_number = re.search(r'"speed_number"\s*:\s*(\d+)', block)
                limit_speed = re.search(r'"limit_speed"\s*:\s*true', block, re.IGNORECASE)
                if speed_number:
                    local_actions.append(f'Set(Expected_speed, {speed_number.group(1)}km/h)')
                elif limit_speed:
                    local_actions.append('Set(Expected_speed, posted_limit_speed)')

            change_lane_blocks = re.findall(r'"Change_lane_action"\s*:\s*{(.*?)}', action_str, re.DOTALL)
            for block in change_lane_blocks:
                direction = re.search(r'"direction"\s*:\s*"([^"]+)"', block)
                times = re.search(r'"times"\s*:\s*(\d+)', block)
                if direction and times:
                    local_actions.append(f'Change_lane({direction.group(1)}, {times.group(1)})')
            
            borrow_lane = re.findall(r'"Whether_allow_left_lane_change"\s*:\s*(true|false)', action_str, re.IGNORECASE)
            for block in borrow_lane:
                local_actions.append(f'Set(Whether_allow_borrow_lane(left), {val.capitalize()})')

            borrow_lane = re.findall(r'"Whether_allow_right_lane_change"\s*:\s*(true|false)', action_str, re.IGNORECASE)
            for block in borrow_lane:
                local_actions.append(f'Set(Whether_allow_borrow_lane(right), {val.capitalize()})')

            
            all_pairs = re.findall(r'"([^"]+)"\s*:\s*(true|false|\d+|"(?:[^"]*)")', action_str)
            known_keys= {"Whether_priority_change_lane", "Whether_allow_u_turn", "Whether_allow_reverse", "Whether_declearation", "Whether_red_light_turn_right", "Whether_allow_left_lane_change", "Whether_allow_right_lane_change", "Whether_stop_before_entering_uncontrolled_intersection", "Whether_allow_parking", "Forward_buffer_distance", "Backward_buffer_distance", "Lateral_buffer_distance", "Dynamic_Obstacle_Follow_distance", "Dynamic_Obstacle_Overtake_distance", "Dynamic_Obstacle_Overtake_distance", "Min_stop_distance", "Static_Obstacle_Deceleration_ratio", "Dynamic_Obstacle_Deceleration_ratio", "Min_speed_for_keep_clear", "Time_interval_for_lane_change", "Check_distance"}
            for key, value in all_pairs:
                if key in known_keys:
                    if value.lower() == 'true':
                        local_actions.append(f'Set({key}, true)')
                    elif value.lower() == 'false':
                        local_actions.append(f'Set({key}, false)')
                    elif re.match(r'^\d+$', value):
                        local_actions.append(f'Set({key}, {value})')
                    else:
                        local_actions.append(f'Set({key}, {value})')
            return local_actions

        def extract_json_objects_from_array(text):
            blocks = []
            buffer = ''
            depth = 0
            inside = False

            for ch in text:
                if ch == '{':
                    depth += 1
                    inside = True
                if inside:
                    buffer += ch
                if ch == '}':
                    depth -= 1
                    if depth == 0 and buffer:
                        blocks.append(buffer.strip())
                        buffer = ''
                        inside = False

            return blocks

        if action_raw.startswith("{"):
            actions.extend(parse_action_dict(action_raw))
        elif action_raw.startswith("["):
            blocks = extract_json_objects_from_array(action_raw)
            for block in blocks:
                if block.startswith("{"):
                    actions.extend(parse_action_dict(block))
                else:
                    print(f"Error: Unexpected block format: {block}")

    # ------- 合成 DSL -------
    dsl = ""
    if trigger_dsl and actions:
        for i in actions:
            dsl += f"trigger\n    {trigger_dsl}"
            if condition_dsl:
                dsl += f"\ncondition\n    {condition_dsl}"
            dsl += f"\nthen\n    {i}\nend\n\n"
        return dsl
    print(f"Error: {raw_str}")
    return None

if __name__ == "__main__":
    file = "Records/China_spec/GPT4.1_patterns.txt"
    standardized_blocks = extract_fuzzy_function_blocks(file)
    standardized_blocks = [extract_dsl_from_raw_string(i) for i in standardized_blocks]
    with open("standardized_output.txt", "w", encoding="utf-8") as f:
        for e, i in enumerate(standardized_blocks):
            f.write(f"--- Function {e} ---\n")
            f.write(i + "\n")
    