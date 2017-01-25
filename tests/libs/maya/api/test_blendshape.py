from maya.api import OpenMaya as om2
from maya import cmds
from tests import mayatestutils

from zoo.libs.maya.api import nodes
from zoo.libs.maya.api import blendshape


class TestBlendshape(mayatestutils.BaseMayaTest):
    application = "maya"

    def createBlendshape(self):
        base = nodes.asMObject(cmds.polyCube(ch=False)[0])
        target = nodes.asMObject(cmds.polyCube(ch=False)[0])
        blendshapeNode = nodes.asMObject(cmds.blendShape(base, target))
        return base, target, blendshapeNode

    def setUp(self):
        self.base, self.target, self.node = self.createBlendshape()
        self.blendshape = blendshape.BlendShapeNode(self.node)
    # def test_baseObjects(self):
    #     pass
    #
    # @utilities.withUndo
    # def test_rename(self):
    #     pass
    #
    # def test_targetCount(self):
    #     pass
    #
    # def test_envelope(self):
    #     pass
    #
    # @utilities.withUndo
    # def test_setEnvelope(self):
    #     pass
    #
    # @utilities.withUndo
    # def test_renameTarget(self):
    #     pass
    #
    # def test_iterTargetIndexPairs(self):
    #     pass
    #
    # def test_targets(self):
    #     pass
    #
    # def test_targetGroupPlug(self):
    #     pass
    #
    # def test_targetInbetweenPlug(self):
    #     pass
    #
    # def test_targetIdxByName(self):
    #     pass
    #
    # def test_targetInbetweenName(self):
    #     pass
    #
    # def test_setTargetInbetweenName(self):
    #     pass
    #
    # def test_targetIndexWeights(self):
    #     pass
    #
    # def test_targetWeights(self):
    #     pass
    #
    # def test_targetPaintWeights(self):
    #     pass
    #
    # def test_basePaintWeights(self):
    #     pass
    #
    # @utilities.withUndo
    # def test_setTargetWeights(self):
    #     pass
    #
    # @utilities.withUndo
    # def test_setTargetWeightValue(self):
    #     pass
    #
    # @utilities.withUndo
    # def test_setBasePaintWeights(self):
    #     pass
    #
    # @utilities.withUndo
    # def test_setTargetPaintWeights(self):
    #     pass
    #
    # @utilities.withUndo
    # def test_addTarget(self):
    #     pass
    #
    # @utilities.withUndo
    # def test_extract(self):
    #     pass
    #
    # @utilities.withUndo
    # def test_extractAll(self):
    #     pass
    #
    # @utilities.withUndo
    # def test_transfer(self):
    #     pass
    #
    # @utilities.withUndo
    # def test_transferPartial(self):
    #     pass
    #
    # def test_TargetExtractContext(self):
    #     pass
