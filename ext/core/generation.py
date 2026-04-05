from .names import CoreLabels
from ..pipeline.registry import OperationRegistry

from ..ui.pipe_schema import PipeSchemaRegistry

import json
from dataclasses import dataclass

import random
import os

from bpy.types import Operator
import bpy

@dataclass
class ExecutionParameters:
    seed: int


class GenerateOperator(Operator):
    """Main operator that reads the config and runs the render loop"""

    bl_idname = CoreLabels.GENERATE.value
    bl_label = "Generate Dataset"

    @staticmethod
    def extract_relevant_data(context) -> ExecutionParameters:
        return ExecutionParameters(1)

    def execute(self, context):
        """Get all selected nodes"""

        scene = context.scene
        # Deserialized all pipes only ones, preparing for thousands of generations poissbly.
        executor = PipelineExecutor(scene)
        executor.compile_pipeline(scene)

        return { 'FINISHED' }


class PipelineExecutor:
    """Compiled, reusable pipeline executor"""

    def __init__(self, scene):
        self.scene = scene
        self.compiled_ops = []

    def compile_pipeline(self, scene) -> list:
        """Deserialize all operations once"""
        pipeline = scene.pipeline_data
        compiled = []

        for operation in pipeline.operations:
            if not operation.enabled:
                continue

            op_type = operation.operation_type

            # Get schema to validate config
            schema = PipeSchemaRegistry.get(op_type)
            if not schema:
                continue

            # Deserialize config
            try:
                config = json.loads(operation.config)
            except json.JSONDecodeError as e:
                print(f"Failed to parse config for {op_type}: {e}")
                continue

            # Get executor class
            try:
                executor_cls = OperationRegistry.get(op_type)
            except ValueError:
                print(f"No executor for {op_type}")
                continue

            compiled.append({
                'name': operation.name,
                'type': op_type,
                'config': config,
                'executor': executor_cls
            })

        self.compiled_ops = compiled
        return compiled

    def execute(self, scene, objects):
        """Execute all compiled operations"""
        for op_data in self.compiled_ops:
            executor = op_data['executor']
            config = op_data['config']

            try:
                executor.execute(scene, objects, config)
            except Exception as e:
                print(f"Error executing {op_data['name']}: {e}")
                # Continue on error or fail? Your choice
                raise


class GenerateDatasetOperator(Operator):
    bl_idname = "randomizer.generate"
    bl_label = "Generate Dataset"

    def execute(self, context):
        scene = context.scene
        num_samples = scene.randomizer_amount
        output_dir = scene.randomizer_destination_path
        seed_value = scene.randomizer_seed

        # Validate
        if not output_dir:
            self.report({'ERROR'}, "Output directory not set")
            return {'CANCELLED'}

        if not scene.pipeline_data.operations:
            self.report({'WARNING'}, "Pipeline is empty")
            return {'CANCELLED'}

        # Create output dir
        os.makedirs(output_dir, exist_ok=True)

        target_objects = context.selected_objects
        if not target_objects:
            self.report({'ERROR'}, "No objects selected")
            return {'CANCELLED'}

        try:
            # Compile pipeline once
            pipeline = PipelineExecutor(scene)
            random.seed(seed_value)

            # Generate frames
            for frame_idx in range(num_samples):

                # Set frame number (for animation if needed)
                scene.frame_set(frame_idx)

                # Apply randomization
                pipeline.execute(scene, target_objects)

                # Render
                filepath = os.path.join(output_dir, f"render_{frame_idx:04d}.png")
                scene.render.filepath = filepath
                bpy.ops.render.render(write_still=True)

                if frame_idx % 10 == 0:
                    print(f"Generated {frame_idx}/{num_samples}")

            self.report({'INFO'}, f"Successfully generated {num_samples} frames to {output_dir}")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Generation failed: {str(e)}")
            return {'CANCELLED'}