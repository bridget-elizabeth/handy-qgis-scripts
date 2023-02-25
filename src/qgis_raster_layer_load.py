"""

        Facilitates reviewing many raster layers in QGIS by:
        
          -  Duplicating each raster map layer currently loaded in the QGIS Layer Panel, then;
          -  Grouping each set of two layers within a sub-group (named with raster filename minus extension);
          -  Setting the symbology for each layer (Top Layer, Bottom Layer) from input .qml file paths
          -  Collapsing all layers & groups
          -  Toggling on "mutually exclusive" visibility of Parent group.
        
    ** Note, assumes raster layers are within one parent group.
    
    Boolean variable values below control execution flow:
        
          - dup_execute             (execution, layer duplication)
          
          - toggle_vis, recursive   (execution, layer visibility)
          - visibility_on           (1 = visibility on, 0 = off)
          - recursive               (1 = apply to all layers within groups & sub-groups)
          
          - exclusive               (execute, mutually exclusive visibility)
          - exclusivity_on          (1 = exclusivity on, 0 = off)    
    
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
dup_execute = 1   # toggle on/off executing layer duplication

toggle_vis = 1    # execute group and layer visibility
visibility_on = 1 # toggle on/off
recursive = 0     # ... layers within sub-groups visibility

exclusive = 1      # execute "mutually exclusive" visibility
exclusivity_on = 1 # toggle on/off

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
        
def set_exclusive(root, exclusive=exclusivity_on, rec=False):
    # set each group to be mutually exclusive
    for group in root.findGroups():
        group.setIsMutuallyExclusive(exclusive)
        
        # set sub-groups if 'rec' is True
        if rec:    
            for subgroup in group.findGroups():   
                subgroup.setIsMutuallyExclusive(exclusive)

def group_visibility(root, vis_on):
    # traverse the tree; toggle visibility of the second layer within each sub-group of the parent group
    for group in root.findGroups():
        for subgroup in group.findGroups():
            subgroup_layers = subgroup.findLayers()
            bottom_layer = subgroup_layers[1]
            bottom_layer.setItemVisibilityChecked(vis_on)
    
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
    group_visibility(root, vis_on=visibility_on)
            
if exclusive:
    set_exclusive(root, exclusive=exclusivity_on, rec=recursive)

