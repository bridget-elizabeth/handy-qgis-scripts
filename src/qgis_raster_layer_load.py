"""

        Facilitates reviewing many raster layers in QGIS by:
        
          -  Duplicating each raster map layer currently loaded in the QGIS Layer Panel, then;
          -  Grouping each set of two layers within a sub-group (named with raster filename minus extension);
          -  Setting the symbology for each layer (Top Layer, Bottom Layer) from input .qml file paths
          -  Collapsing all layers & groups
          -  Toggling on "mutually exclusive" visibility of Parent group.
        
    ** Note, assumes raster layers are within one parent group.
    
    Boolean variable values below control execution flow:
        
          - dup_execute             (layer duplication)
          - toggle_vis, recursive   (layer visibility)
          - exclusive               (mutually exclusive visibility)
    
"""

import re
from qgis.core import QgsProject, QgsLayerTreeGroup, QgsMapLayer, QgsRasterLayer

# -----------
# set .qml symbology filepaths
# -----------
sym_above = r'hillshade_topLayer.qml'
sym_below = r'hillshade_BottomLayer.qml'

# -----------
# execute 
# -----------
dup_execute = 1  # toggle on/off executing layer duplication

toggle_vis = 1   # toggle on/off group and layer visibility
recursive = 0   # toggle on/off for layers within sub-groups visibility

exclusive = 1    # toggle on/off "mutually exclusive" visibility

# --------
# helpers
# --------

# --- collapse all layers ---
def collapse_layers(root):
    for layer in root.findLayers():
        layer.setExpanded(False)
        
# --- collapse all groups ---        
def collapse_groups(root):
    for group in root.findGroups():
        group.setExpanded(False)
        for subgroup in group.findGroups():
            subgroup.setExpanded(False)
        
def set_exclusive(root, turn_on=True, rec=False):
    # set each group to be mutually exclusive
    for group in root.findGroups():
        group.setIsMutuallyExclusive(turn_on)
        
        # set sub-groups if 'rec' is True
        if rec:    
            for subgroup in group.findGroups():   
                subgroup.setIsMutuallyExclusive(turn_on)

def group_visibility(root, turn_on=False):
    # traverse the tree; toggle visibility of the second layer within each sub-group of the parent group
    for group in root.findGroups():
        for subgroup in group.findGroups():
            subgroup_layers = subgroup.findLayers()
            bottom_layer = subgroup_layers[1]
            bottom_layer.setItemVisibilityChecked(turn_on)
    
# --- **note, assumes all layers are within a parent group; duplicates each layer, sub-groups the two layers, applies symbology from .qml
def raster_dup(root, sym_above, sym_below):
    for group in root.findGroups():
        for layer in group.findLayers():

            # create new Group
            new_group = group.insertGroup(0, layer.name())
       
            # duplicate Raster Layer
            baselayer = QgsProject.instance().mapLayersByName(layer.name())[0]
            dup_layer = QgsRasterLayer(baselayer.source(), baselayer.name()+'_Copy')
            
            # add Dup-Layer to Map
            QgsProject.instance().addMapLayer(dup_layer, False)
            
            # apply symbology to layers from .qml files
            baselayer.loadNamedStyle(sym_above)
            dup_layer.loadNamedStyle(sym_below)
            
            # insert Layer into Group
            new_group.addLayer(baselayer)
            # insert Dup-Layer into Group
            new_group.addLayer(dup_layer)
            
            # remove initial layers (now duplicates)
            group.removeChildNode(layer)

    
# -----------
# execution
# -----------
root = QgsProject.instance().layerTreeRoot()

# traverse & collapse
collapse_layers(root)

# duplicate & group
if dup_execute:
    
    raster_dup(root, sym_above, sym_below)

    # traverse & collapse
    collapse_layers(root)
    collapse_groups(root)

# visibility
if toggle_vis:
    group_visibility(root, turn_on=0)
            
if exclusive:
    set_exclusive(root, turn_on=1, rec=recursive)

