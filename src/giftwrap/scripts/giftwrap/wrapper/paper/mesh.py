import maya.cmds as cmds
import maya.mel as mel

class PaperMesh:
    """
    Creates a wrapping paper mesh which is then controlled by the
    folding plane using a wrap deformer.
    """
    def __init__(self, folding_plane, paper_thickness, wrap_id):
        self.plane = folding_plane.getTransformNode()
        self.thickness = paper_thickness
        self.wrap_id = wrap_id

        self.mesh = cmds.duplicate(self.plane,
                                   name=f'wrap_paper_{self.wrap_id}')
        print(f'paper mesh dup: {self.mesh}')
        self.mesh = self.mesh[0]

        # Make high-poly
        cmds.polyBevel(self.mesh, offset=0.005, constructionHistory=0)
        cmds.polySubdivideFacet(self.mesh, divisions=1, divisionsV=1,
                                subdMethod=0, constructionHistory=0)

        # Move pivot, translate, add thickness
        if self.thickness > 0:
            cmds.move(0, self.thickness / 2, 0, self.mesh + '.rotatePivot',
                      relative=True)
            cmds.setAttr(self.mesh + '.translateY', -0.5 * self.thickness)

            cmds.polyExtrudeFacet(self.mesh, translateY=(self.thickness * 1),
                                  constructionHistory=0)

        # UV mapping
        num_verts = cmds.polyEvaluate(self.mesh, face=True) - 1
        eval_this = ('polyProjection -ch 0 -type Planar -ibd on -kir -md y ' +
                     f'{self.mesh}.f[0:{num_verts}]')
        mel.eval(eval_this)  # UV planar map

    def getTransformNode(self):
        return self.mesh

