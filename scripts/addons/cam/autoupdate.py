from datetime import date
from cam.version import __version__ as current_version
from urllib.request import urlopen
import json
import pathlib
import zipfile
import bpy
import re
import io
import os
import sys

class UpdateChecker(bpy.types.Operator):
    """calculate all CAM paths"""
    bl_idname = "render.cam_check_updates"
    bl_label = "Check for updates in blendercam plugin"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        last_update_check = bpy.context.preferences.addons['cam'].preferences.last_update_check
        today=date.today().toordinal()
        if last_update_check!=today or True: # TODO: remove after testing
            update_source = bpy.context.preferences.addons['cam'].preferences.update_source
            # get list of releases from github release
            if update_source.endswith("/releases"):
                with urlopen(update_source) as response:
                    body = response.read().decode("UTF-8")
                    # find the tag name
                    release_list=json.loads(body)
                    if len(release_list) > 0:
                        release = release_list[0]
                        tag = release["tag_name"]
                        print(f"Found release: {tag}")
                        match = re.match(r".*(\d+)\.(\s*\d+)\.(\s*\d+)",tag)
                        if match:
                            version_num  = tuple(map(int,match.groups()))
                            print(f"Found version: {version_num}")
                            bpy.context.preferences.addons['cam'].preferences.last_update_check = today
                            bpy.ops.wm.save_userpref()

                            if version_num > current_version:
                                print("Version is newer, downloading source")
                                zip_url = release["zipball_url"]
                                with urlopen(zip_url) as zip_response:
                                    zip_body=zip_response.read()
                                    buffer= io.BytesIO(zip_body)
                                    zf=zipfile.ZipFile(buffer,mode='r')
                                    files=zf.infolist()
                                    cam_addon_path = pathlib.Path(__file__).parent
                                    for fileinfo in files:
                                        filename=fileinfo.filename
                                        if fileinfo.is_dir() == False:
                                            path_pos=filename.replace("\\","/").find("/scripts/addons/cam/")
                                            if path_pos!=-1:
                                                relative_path=filename[path_pos+len("/scripts/addons/cam/"):]
                                                out_path = addons_path / relative_path
                                                print(out_path)
                                                # check folder exists
                                                out_path.parent.mkdir(parents=True,exist_ok=True)
                                                with zf.open(filename,"r") as in_file, open(out_path,"wb") as out_file:
                                                    out_file.write(in_file.read())
                                                # TODO: what about if a file is deleted...
                                    # updated everything, now mark as updated and reload scripts
                                    bpy.context.preferences.addons['cam'].preferences.just_updated=True
                                    # unload ourself from python module system
                                    delete_list=[]
                                    for m in sys.modules.keys():
                                        if m.startswith("cam.") or m=='cam':
                                            delete_list.append(m)
                                    for d in delete_list:
                                        del sys.modules[d]
                                    bpy.ops.wm.save_userpref()
                                    bpy.ops.script.reload()
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop_search(self, "operation", bpy.context.scene, "cam_operations")

