import os
import json
import platform
import subprocess
import io
from contextlib import redirect_stdout

from bpy.types import Operator
from bpy.props import StringProperty

from ..utils.logger import UniqueLogger

import bpy

class LoadPipelineOperator(Operator):

    bl_idname = "randomizer.load_pipeline"
    bl_label = "Load Pipeline"

    def execute(self, context):
        """Capture undo history by redirecting stdout"""

        f = io.StringIO()
        with redirect_stdout(f):
            context.window_manager.print_undo_steps()

        output = f.getvalue()
        UniqueLogger.quick_log(output)
        return {'FINISHED'}

class SavePipelineAsOperator(Operator):

    bl_idname = "randomizer.save_pipeline"
    bl_label = "Write back the pipeline"

    filepath: StringProperty(subtype='FILE_PATH', default='pipeline.json')          # type: ignore

    def execute(self, context):
        try:
            pipeline = context.scene.pipeline_data

            pipeline_dict = {
                'version': '1.0',
                'operations': [
                    {
                        'operation_type': op.operation_type,
                        'seed': op.seed,
                        'intensity': op.intensity,
                        'enabled': op.enabled,
                    }
                    for op in pipeline.operations
                ]
            }

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)

            with open(self.filepath, 'w') as f:
                json.dump(pipeline_dict, f, indent=2)

            # Save the save path
            context.scene.randomizer_pipeline_save_path = self.filepath

            # Clear unsaved changes flag
            context.scene.pipeline_has_unsaved_changes = False

            self.report({'INFO'}, f'Saved pipeline to {self.filepath}')
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f'Failed to save: {str(e)}')
            return {'CANCELLED'}

    def invoke(self, context, _):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class OpenLogsOperator(Operator):
    """Open the log file in default editor"""
    bl_idname = "randomizer.open_log_file"
    bl_label = "Open Log File"

    def execute(self, _context):
        """

        :param _context:
        :return:
        """

        if not UniqueLogger.available():
            self.report({ 'ERROR' }, "Log file does not exist.")
            return { 'CANCELLED' }

        # Open file with default app
        log_path = UniqueLogger.get_path()
        try:
            if platform.system() == "Windows":
                os.startfile(log_path)
            # https://wenku.csdn.net/answer/3pg0xo8hc0
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", log_path])
            else:  # Linux
                subprocess.Popen(["xdg-open", log_path])

        except Exception as e:
            self.report({ 'ERROR' }, f"Could not open log file: {e}.")

        return { 'FINISHED' }



def setup_logger_from_scene(context) -> bool:
    """ Setup logger using scene property """

    try:
        # Clean up the previous logger, e.g. generate a new writing path
        UniqueLogger.cleanup()
        # Now set up the new logger which sets multiple logger variables (the path,
        # the availability of the logger with UniqueLogger.available()
        directory = context.scene.randomizer_logging_path
        UniqueLogger.initialize_logging(directory)
        return True

    except Exception as e:
        context.report({ 'ERROR' }, f"Could not setup logger: {e}.")
        return False


class ApplyLogPathOperator(Operator):
    bl_idname = "randomizer.setup_log"
    bl_label = "Apply Log Path"

    def execute(self, context):
        """

        :param context:
        :return:
        """
        if setup_logger_from_scene(context):
            self.report({'INFO'}, "Logger updated!")
            return { 'FINISHED' }
        else:
            self.report({'ERROR'}, "Failed to update logger")
            return { 'CANCELLED' }
