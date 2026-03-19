import os
import json
import os.path as path
from datetime import datetime
import logging
import platform
import subprocess

from bpy.types import Operator
from bpy.props import StringProperty


class LoadPipelineOperator(Operator):

    bl_idname = "randomizer.load_pipeline"
    bl_label = "Load Pipeline"

    def execute(self, context):
        pass

class SavePipelineAsOperator(Operator):

    bl_idname = "randomizer.save_pipeline"
    bl_label = "Write back the pipeline"

    filepath: StringProperty(subtype='FILE_PATH', default='pipeline.json')

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
        global current_log_file

        if not os.path.exists(current_log_file):
            self.report({'ERROR'}, "Log file does not exist.")
            return { 'CANCELLED' }

        # Open file with default app
        try:
            if platform.system() == "Windows":
                os.startfile(current_log_file)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", current_log_file])
            else:  # Linux
                subprocess.Popen(["xdg-open", current_log_file])

        except Exception as e:
            self.report({ 'ERROR' }, f"Could not open log file: {e}")

        return { 'FINISHED' }



def setup_logger_from_scene(context):
    """ Setup logger using scene property """
    global logger
    global current_log_file

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_path = os.path.join(context.scene.randomizer_logging_path, f"logs_{timestamp}.txt")
    current_log_file = log_path

    # Remove existing handlers
    if logger:
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    logger = logging.getLogger("default_logger")
    logger.setLevel(logging.DEBUG)

    try:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            '%(asctime)s - [%(levelname)s] - %(message)s'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        logger.info(f"Completed logger setup: {log_path}")
        return True

    except Exception as e:
        context.report({'ERROR'}, f"Could not setup logger: {e}")
        return False


class ApplyLogPathOperator(Operator):
    bl_idname = "randomizer.setup_log"
    bl_label = "Apply Log Path"

    def execute(self, context):
        if setup_logger_from_scene(context):
            self.report({'INFO'}, "Logger updated!")
            return { 'FINISHED' }
        else:
            self.report({'ERROR'}, "Failed to update logger")
            return { 'CANCELLED' }
