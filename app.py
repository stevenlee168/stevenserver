from flask import Flask, render_template, request, jsonify
from datetime import datetime
import re
import os
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Đảm bảo thư mục uploads tồn tại
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Trang chính
@app.route('/')
def index():
    return render_template('index.html')

# Trang tiện ích (utility pages) như lasercutting.html, etc.
@app.route('/utility/<page>')
def utility_page(page):
    try:
        return render_template(f'utility/{page}')
    except:
        return "Unexpected Error", 404

#Welding URL
@app.route("/process-file-welding", methods=["POST"])
def process_file_w_URL():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        moveAbs = request.form.get('moveAbs')
        moveJ = request.form.get('moveJ')
        moveL = request.form.get('moveL')
        moveC = request.form.get('moveC')
        zoneAbs = request.form.get('zoneAbs')
        zoneJ = request.form.get('zoneJ')
        zoneL = request.form.get('zoneL')
        zoneC = request.form.get('zoneC')
        tool = request.form.get('tool')
        userframe = request.form.get('userframe')
        
        if not file:#file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # Lưu file tạm
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Đọc nội dung file
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        result = process_file_w(
            content,
            moveAbs=moveAbs,
            moveJ=moveJ,
            moveL=moveL,
            moveC=moveC,
            zoneAbs=zoneAbs,
            zoneJ=zoneJ,
            zoneL=zoneL,
            zoneC=zoneC,
            tool=tool,
            userframe=userframe
        )
        #result = process_content_upper(content)
        return jsonify({"processedText": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
#Welding URL
@app.route("/process-file-deburring", methods=["POST"])
def process_file_db_URL():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        moveAbs = request.form.get('moveAbs')
        moveJ = request.form.get('moveJ')
        moveL = request.form.get('moveL')
        moveC = request.form.get('moveC')
        zoneAbs = request.form.get('zoneAbs')
        zoneJ = request.form.get('zoneJ')
        zoneL = request.form.get('zoneL')
        zoneC = request.form.get('zoneC')
        tool = request.form.get('tool')
        userframe = request.form.get('userframe')
        
        if not file:#file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # Lưu file tạm
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Đọc nội dung file
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        result = process_file_db(
            content,
            moveAbs=moveAbs,
            moveJ=moveJ,
            moveL=moveL,
            moveC=moveC,
            zoneAbs=zoneAbs,
            zoneJ=zoneJ,
            zoneL=zoneL,
            zoneC=zoneC,
            tool=tool,
            userframe=userframe
        )
        #result = process_content_upper(content)
        return jsonify({"processedText": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/process-file-laser", methods=["POST"])
def process_file_laser():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
            
        file = request.files["file"]
        text = file.read().decode("utf-8")

        # paramMap từ bảng
        raw_param_map = request.form.get("paramMap")
        param_map = json.loads(raw_param_map) if raw_param_map else {}
        advance_mode = request.form.get("advanceMode", "false").lower() == "true"
        test_mode = request.form.get("testMode", "false").lower() == "true"
        circle_mode = request.form.get("circleMode", "false").lower() == "true"

        # default values từ HTML input
        defaults = {
            "moveAbs": request.form.get("moveAbs"),
            "moveJ": request.form.get("moveJ"),
            "moveL": request.form.get("moveL"),
            "moveC": request.form.get("moveC"),
            "zoneAbs": request.form.get("zoneAbs"),
            "zoneJ": request.form.get("zoneJ"),
            "zoneL": request.form.get("zoneL"),
            "zoneC": request.form.get("zoneC"),
            "tool": request.form.get("tool"),
            "userframe": request.form.get("userframe"),
        }

        # hàm xử lý
        result = process_file_lct(text, param_map, defaults)
        return jsonify({"processedText": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
# Copyright
def add_copyright_notice(processed_text):
    current_year = datetime.now().year
    copyright_notice = (
f"""  !===============================================================
  !Copyright {current_year} Steven Lee - Da Shiang Automation - DTboost
  !
  !WARNING: This code is the intellectual property of Steven Lee - Da Shiang Automation. 
  !You may NOT modify this code unless you have explicit permission from the author. 
  !Unauthorized modification of this code may result in legal action.
  !
  !DISCLAIMER: The author assumes no responsibility or liability for any modifications made to this code 
  !by third parties. Any modifications are made at the user's own risk and the user assumes all 
  !responsibility for any consequences resulting from such modifications.
  !===============================================================\n"""
    )

    lines = processed_text.split("\n")
    new_text = []

    for line in lines:
        new_text.append(line)
        if line.strip().startswith("MODULE"):
            new_text.append(copyright_notice)
    return "\n".join(new_text)

def add_rtool_adj(text, tool_adj, tool_og):
    lines = text.split("\n")
    new_text = []

    for line in lines:
        new_text.append(line)
        if line.strip().startswith("! ---"):  # Kiểm tra comment bắt đầu với ! ---
            new_text.append(f'    <span class="highlight">{tool_adj}:=Modify_rTCP_Offset({tool_og},0,0,0,0,0,0);</span>')
            # Nếu bạn muốn giữ HTML tag giống JS:
            # new_text.append(f'    <span class="highlight">{tool_adj}:=Modify_rTCP_Offset(rtool_adj(processed_text, tool_adj, tool_og)
    return "\n".join(new_text)

def process_file_w(uploaded_text, moveAbs, moveJ, moveL, moveC,
                 zoneAbs, zoneJ, zoneL, zoneC,
                 tool, userframe):
    if not uploaded_text:
        raise ValueError("No uploaded text provided.")

    tool_adj = tool + '_Adj'
    tool_og = tool

    processed_text = re.sub(r'PERS.*', '!===============================================================', uploaded_text)

    # Update MoveAbsJ
    processed_text = re.sub(
        r'MoveAbsJ\s+\[\[([^\]]+)\],\[([^\]]+)\]\],(\w+),(\w+),(\w+)\\Wobj:=(\w+);',
        fr'MoveAbsJ [[\1],[\2]],{moveAbs},{zoneAbs},{tool_adj}\\Wobj:={userframe};',
        processed_text
    )

    # Update MoveJ
    processed_text = re.sub(
        r'MoveJ\s+\[\[([^\]]+)\],\[([^\]]+)\],\[([^\]]+)\],\[([^\]]+)\]\],\[[^\]]+\],(.*?),(\w+)\\Wobj:=(\w+);',
        fr'MoveJ [[\1],[\2],[\3],[\4]],{moveJ},{zoneJ},{tool_adj}\\Wobj:={userframe};',
        processed_text
    )

    # Update MoveL
    processed_text = re.sub(
        r'MoveL\s+\[\[([^\]]+)\],\[([^\]]+)\],\[([^\]]+)\],\[([^\]]+)\]\],\[[^\]]+\],(.*?),(\w+)\\Wobj:=(\w+);',
        fr'MoveL [[\1],[\2],[\3],[\4]],{moveL},{zoneL},{tool_adj}\\Wobj:={userframe};',
        processed_text
    )

    # Update MoveC
    processed_text = re.sub(
        r'MoveC\s+\[\[([^\]]+)\],\[([^\]]+)\],\[([^\]]+)\],\[([^\]]+)\]\],\[\[([^\]]+)\],\[([^\]]+)\],\[([^\]]+)\],\[([^\]]+)\]\],\[[^\]]+\],(.*?),(\w+)\\Wobj:=(\w+);',
        fr'MoveC [[\1],[\2],[\3],[\4]],[[\5],[\6],[\7],[\8]],{moveC},{zoneC},{tool_adj}\\Wobj:={userframe};',
        processed_text
    )

    # Thêm Tool Adj logic nếu cần
    processed_text = add_rtool_adj(processed_text, tool_adj, tool_og)

    # Thêm copyright notice
    processed_text = add_copyright_notice(processed_text)

    return processed_text

def process_file_db(uploaded_text, moveAbs, moveJ, moveL, moveC,
                 zoneAbs, zoneJ, zoneL, zoneC,
                 tool, userframe):
    if not uploaded_text:
        raise ValueError("No uploaded text provided.")

    tool_adj = tool + '_Adj'
    tool_og = tool

    processed_text = re.sub(r'PERS.*', '!===============================================================', uploaded_text)

    # Update MoveAbsJ
    processed_text = re.sub(
        r'MoveAbsJ\s+\[\[([^\]]+)\],\[([^\]]+)\]\],(\w+),(\w+),(\w+)\\Wobj:=(\w+);',
        fr'MoveAbsJ [[\1],[\2]],{moveAbs},{zoneAbs},{tool_adj}\\Wobj:={userframe};',
        processed_text
    )

    # Update MoveJ
    processed_text = re.sub(
        r'MoveJ\s+\[\[([^\]]+)\],\[([^\]]+)\],\[([^\]]+)\],\[([^\]]+)\]\],\[[^\]]+\],(.*?),(\w+)\\Wobj:=(\w+);',
        fr'MoveJ [[\1],[\2],[\3],[\4]],{moveJ},{zoneJ},{tool_adj}\\Wobj:={userframe};',
        processed_text
    )

    # Update MoveL
    processed_text = re.sub(
        r'MoveL\s+\[\[([^\]]+)\],\[([^\]]+)\],\[([^\]]+)\],\[([^\]]+)\]\],\[[^\]]+\],(.*?),(\w+)\\Wobj:=(\w+);',
        fr'MoveL [[\1],[\2],[\3],[\4]],{moveL},{zoneL},{tool_adj}\\Wobj:={userframe};',
        processed_text
    )

    # Update MoveC
    processed_text = re.sub(
        r'MoveC\s+\[\[([^\]]+)\],\[([^\]]+)\],\[([^\]]+)\],\[([^\]]+)\]\],\[\[([^\]]+)\],\[([^\]]+)\],\[([^\]]+)\],\[([^\]]+)\]\],\[[^\]]+\],(.*?),(\w+)\\Wobj:=(\w+);',
        fr'MoveC [[\1],[\2],[\3],[\4]],[[\5],[\6],[\7],[\8]],{moveC},{zoneC},{tool_adj}\\Wobj:={userframe};',
        processed_text
    )

    # Thêm Tool Adj logic nếu cần
    processed_text = add_rtool_adj(processed_text, tool_adj, tool_og)

    # Thêm copyright notice
    processed_text = add_copyright_notice(processed_text)

    return processed_text

def add_laser_off(text):
    lines = text.split("\n")
    new_lines = []

    for i in range(len(lines)):
        new_lines.append(lines[i])  # luôn giữ dòng hiện tại

        # Nếu dòng hiện tại là MoveL
        if lines[i].strip().startswith("MoveL"):
            # Kiểm tra điều kiện
            if (
                i > 0 and lines[i - 1].strip().startswith("MoveL")  # dòng trước là MoveL
                and i + 1 < len(lines) and lines[i + 1].strip().startswith("MoveL")  # dòng sau là MoveL
                and i + 2 < len(lines) and lines[i + 2].strip().startswith("MoveJ")  # dòng sau nữa là MoveJ
            ):
                # Chèn Laser_Off
                new_lines.append('    <span class="highlight">Laser_Off;</span>')

    return "\n".join(new_lines)

def add_laser_process_param(text, param_map, laser_prc_par):
    """
    Thêm Laser_Process_Param_In vào sau MoveL khi:
    - Trước MoveL là Laser_Punch_Cir_* và sau là MoveL => thêm 'Laser_Process_Param_In 25;'
    - Trước MoveL là Laser_Punch_* và sau là MoveL => thêm 'Laser_Process_Param_In {param};'
    """

    lines = text.split("\n")
    new_lines = []
    current_section = ""

    for i, line in enumerate(lines):
        new_lines.append(line)  # giữ dòng hiện tại

        # Track current section title
        if line.strip().startswith("! ---"):
            current_section = (
                line.replace("! ---", "").replace("---", "").strip().lower()
            )

        # Nếu là MoveL
        if line.strip().startswith("MoveL"):
            prev_line = lines[i - 1].strip() if i > 0 else ""
            next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
            param = param_map.get(current_section, laser_prc_par)  # default

            if prev_line.startswith("Laser_Punch_Cir_") and next_line.startswith("MoveL"):
                new_lines.append("    Laser_Process_Param_In 25;")
            elif prev_line.startswith("Laser_Punch_") and next_line.startswith("MoveL"):
                new_lines.append(f"    Laser_Process_Param_In {param};")

    return "\n".join(new_lines)

def add_laser_punch_param(text, param_map, laser_pch_par, is_cir_mode):
    """
    Thêm Laser_Punch_Param_In vào sau MoveL khi:
    - Nếu is_cir_mode == True và:
        + trong 5~7 dòng trước có chứa '! --- Cir'
        + dòng trước là MoveJ
        + dòng sau là MoveL
      => thêm 'Laser_Punch_Cir_Param_In 25;'
    - Nếu:
        + dòng trước là MoveJ
        + dòng sau là MoveL
      => thêm 'Laser_Punch_Param_In {param};'
    """

    lines = text.split("\n")
    new_lines = []
    current_section = ""

    for i, line in enumerate(lines):
        new_lines.append(line)  # giữ dòng hiện tại

        # Track current section title
        if line.strip().startswith("! ---"):
            current_section = (
                line.replace("! ---", "").replace("---", "").strip().lower()
            )

        if line.strip().startswith("MoveL"):
            param = param_map.get(current_section, laser_pch_par)  # default
            prev_line = lines[i - 1].strip() if i > 0 else ""
            prev_line5 = lines[i - 5].strip() if i > 4 else ""
            prev_line6 = lines[i - 6].strip() if i > 5 else ""
            prev_line7 = lines[i - 7].strip() if i > 6 else ""
            next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""

            if (
                is_cir_mode
                and (
                    prev_line5.startswith("! --- Cir")
                    or prev_line6.startswith("! --- Cir")
                    or prev_line7.startswith("! --- Cir")
                )
                and prev_line.startswith("MoveJ")
                and next_line.startswith("MoveL")
            ):
                new_lines.append("    Laser_Punch_Cir_Param_In 25;")
            elif prev_line.startswith("MoveJ") and next_line.startswith("MoveL"):
                new_lines.append(f"    Laser_Punch_Param_In {param};")

    return "\n".join(new_lines)

def add_laser_speed_param(text, param_map, uf, uf_adj, laser_spd_par, is_advance_mode, is_cir_mode):
    """
    Thêm Laser_Speed_Param_In sau khi gặp comment và dòng MoveJ ngay sau nó.
    - Nếu is_advance_mode = True: thêm Modify_DYN_Wobj_Offset
    - Nếu comment bắt đầu bằng '! --- Cir' và is_cir_mode = True:
        thêm Laser_Speed_Param_In 25
    - Ngược lại:
        thêm Laser_Speed_Param_In {param} (lấy từ param_map hoặc default = laser_spd_par)
    """

    lines = text.split("\n")
    new_lines = []
    current_section = ""

    for i, line in enumerate(lines):
        new_lines.append(line)

        # Check for new section
        if line.strip().startswith("! ---"):
            current_section = (
                line.replace("! ---", "").replace("---", "").strip().lower()
            )

        # Nếu dòng này là comment, và dòng sau có chứa MoveJ
        if line.strip().startswith("!") and i + 1 < len(lines) and "MoveJ" in lines[i + 1]:
            param = param_map.get(current_section, laser_spd_par)

            if is_advance_mode:
                new_lines.append(
                    f"    {uf_adj}:=Modify_DYN_Wobj_Offset({uf},0,0,0,0,0,0);"
                )

            if line.strip().startswith("! --- Cir") and is_cir_mode:
                new_lines.append("    Laser_Speed_Param_In 25;")
            else:
                new_lines.append(f"    Laser_Speed_Param_In {param};")

    return "\n".join(new_lines)

def process_file_lct(text, param_map, defaults):
    print(param_map)
    return
    
# Chạy server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)































