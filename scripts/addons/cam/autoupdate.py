from datetime import date
from cam.version import __version__ as current_version
from urllib.request import urlopen
import json
import pathlib
import zipfile
import bpy

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
                    release_list=json.reads(body)
                    if len(release_list) > 0:
                        release = release_list[0]
                        tag = release["tag_name"]
                        print(f"Found release: {tag}")
                        match = re.match(r".*\(\s*(\d+),(\s*\d+),(\s*\d+)\)",tag)
                        if match:
                            version_num  = map(int,match.groups())                                
                            print(f"Found release: {version_num}")
                            if version_num > current_version:
                                print("Version is newer, downloading source")
                                zip_url = zipball_url
                                with urlopen(zipball_url) as zip_response:
                                    zip_body=zip_response.read()
                                    zf=zipfile.ZipFile(buffer,mode='r')
                                    files=zf.infolist()
                                    addons_path = pathlib.Path(__file__).parent.parent
                                    for fileinfo in files:
                                        filename=fileinfo.filename
                                        path= zipfile.Path(zf,filename)
                                        parent_path=path.parents[-4]
                                        if path.is_file() and parent_path.match("/*/scripts/addons"):
                                            # path is under scripts/addons, copy it into our addon folder
                                            relative_path = path.relative_to(parent_path)
                                            out_path = addons_path.joinpath(relative_path)
                                            # check folder exists
                                            out_path.parent.mkdir(parents=True,exist_ok=True)
                                            zf.extract(path,path=out_path)
                                        # TODO: what about if a file is deleted...
                                    # updated everything, now mark as updated and reload scripts
                                    bpy.context.preferences.addons['cam'].preferences.just_updated=True
                                    bpy.ops.wm.save_userpref()
                                    bpy.ops.script.reload()
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop_search(self, "operation", bpy.context.scene, "cam_operations")

