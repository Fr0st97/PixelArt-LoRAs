"""Lets ComfyUI load this repository as a custom node pack (clone it into ComfyUI/custom_nodes/). The node itself is in
comfyui/nodes.py; outside ComfyUI this file is not used."""
from .comfyui.nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
