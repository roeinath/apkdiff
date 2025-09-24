from flask import send_from_directory, abort
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, abort
from werkzeug.utils import secure_filename
import os
import json
from .analysis import analyze_apk, compare_apks


bp = Blueprint('main', __name__)

@bp.route('/view_json/<filename>')
def view_json(filename):
    upload_dir = os.path.join(os.path.dirname(__file__), 'uploads')
    json_path = os.path.join(upload_dir, filename)
    if not os.path.exists(json_path) or not filename.endswith('.json'):
        abort(404)
    with open(json_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except Exception:
            data = f.read()
    return render_template('view_json.html', filename=filename, data=data)

def get_uploaded_files():
    upload_dir = os.path.join(os.path.dirname(__file__), 'uploads')
    files = os.listdir(upload_dir)
    apks = [f for f in files if f.endswith('.apk')]
    jsons = [f for f in files if f.endswith('.json')]
    # Associate JSONs to APKs by base name (before extension)
    apk_map = {}
    for apk in apks:
        base = os.path.splitext(apk)[0]
        # Find json with same base name
        json_match = next((j for j in jsons if os.path.splitext(j)[0] == base), None)
        apk_map[apk] = json_match
    return apk_map

@bp.route('/list_apks')
def list_apks():
    apk_map = get_uploaded_files()
    return render_template('list_apks.html', apk_map=apk_map)


@bp.route('/', methods=['GET', 'POST'])
def upload_apk():
    if request.method == 'POST':
        apk_file = request.files.get('apkfile')
        json_file = request.files.get('jsonfile')
        if not apk_file or apk_file.filename == '':
            flash('No APK file selected')
            return redirect(request.url)
        if not json_file or json_file.filename == '':
            flash('No JSON file selected')
            return redirect(request.url)
        if not apk_file.filename.endswith('.apk'):
            flash('Invalid APK file type')
            return redirect(request.url)
        if not json_file.filename.endswith('.json'):
            flash('Invalid JSON file type')
            return redirect(request.url)
        apk_filename = secure_filename(apk_file.filename)
        json_filename = secure_filename(json_file.filename)
        upload_dir = os.path.join(os.path.dirname(__file__), 'uploads')
        apk_path = os.path.join(upload_dir, apk_filename)
        json_path = os.path.join(upload_dir, json_filename)
        apk_file.save(apk_path)
        json_file.save(json_path)
        # Optionally, store association in a manifest file or DB
        results = analyze_apk(apk_path)
        return render_template('result.html', results=results)
    return render_template('upload.html')

@bp.route('/compare', methods=['GET', 'POST'])
def compare_apk():
    if request.method == 'POST':
        file1 = request.files.get('apkfile1')
        file2 = request.files.get('apkfile2')
        if not file1 or not file2 or file1.filename == '' or file2.filename == '':
            flash('Please select two APK files')
            return redirect(request.url)
        if file1.filename.endswith('.apk') and file2.filename.endswith('.apk'):
            filename1 = secure_filename(file1.filename)
            filename2 = secure_filename(file2.filename)
            path1 = os.path.join(os.path.dirname(__file__), 'uploads', filename1)
            path2 = os.path.join(os.path.dirname(__file__), 'uploads', filename2)
            file1.save(path1)
            file2.save(path2)
            results = compare_apks(path1, path2)
            return render_template('result.html', results=results)
        else:
            flash('Invalid file type(s)')
            return redirect(request.url)
    return render_template('compare.html')
