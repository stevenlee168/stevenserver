from flask import Flask, render_template, request, jsonify
from datetime import datetime
import re
import os

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

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    result = process_file(
        uploaded_text=data.get('uploadedText', ''),
        moveAbs=data.get('moveAbs', ''),
        moveJ=data.get('moveJ', ''),
        moveL=data.get('moveL', ''),
        moveC=data.get('moveC', ''),
        zoneAbs=data.get('zoneAbs', ''),
        zoneJ=data.get('zoneJ', ''),
        zoneL=data.get('zoneL', ''),
        zoneC=data.get('zoneC', ''),
        tool=data.get('tool', ''),
        userframe=data.get('userframe', '')
    )
    return jsonify({"processedText": result})

@app.route("/process-file", methods=["POST"])
def process_file_U():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # Lưu file tạm
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Đọc nội dung file
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        data = request.json
        result = process_file(
            uploaded_text=data.get('uploadedText', ''),
            moveAbs=data.get('moveAbs', ''),
            moveJ=data.get('moveJ', ''),
            moveL=data.get('moveL', ''),
            moveC=data.get('moveC', ''),
            zoneAbs=data.get('zoneAbs', ''),
            zoneJ=data.get('zoneJ', ''),
            zoneL=data.get('zoneL', ''),
            zoneC=data.get('zoneC', ''),
            tool=data.get('tool', ''),
            userframe=data.get('userframe', '')
        )
        return jsonify({"processedText": result}

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def process_content_upper(text):
    # Ở đây bạn có thể gọi addToolAdj hoặc addCopyrightNotice
    return text.upper()
    
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

def add_tool_adj(text, tool_adj, tool_og):
    lines = text.split("\n")
    new_text = []

    for line in lines:
        new_text.append(line)
        if line.strip().startswith("! ---"):  # Kiểm tra comment bắt đầu với ! ---
            new_text.append(f'    {tool_adj}:=Modify_rTCP_Offset({tool_og},0,0,0,0,0,0);')
            # Nếu bạn muốn giữ HTML tag giống JS:
            # new_text.append(f'    <span class="highlight">{tool_adj}:=Modify_rTCP_Offset({tool_og},0,0,0,0,0,0);</span>')
    
    return "\n".join(new_text)

def process_file(uploaded_text, moveAbs, moveJ, moveL, moveC,
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
    processed_text = add_tool_adj(processed_text, tool_adj, tool_og)

    # Thêm copyright notice
    processed_text = add_copyright_notice(processed_text)

    return processed_text
    
# Chạy server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)




