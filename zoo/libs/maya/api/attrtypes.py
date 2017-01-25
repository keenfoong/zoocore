from maya.api import OpenMaya as om2
kMFnNumericBoolean = 0
kMFnNumericShort = 1
kMFnNumericInt = 2
kMFnNumericLong = 3
kMFnNumericByte = 3
kMFnNumericFloat = 4
kMFnNumericDouble = 5
kMFnNumericAddr = 6
kMFnNumericChar = 8
kMFnUnitAttributeDistance = 9
kMFnUnitAttributeAngle = 10
kMFnUnitAttributeTime = 11
kMFnkEnumAttribute = 12
kMFnDataString = 13
kMFnDataMatrix = 14
kMFnDataFloatArray = 15
kMFnDataDoubleArray = 16
kMFnDataIntArray = 17
kMFnDataPointArray = 18
kMFnDataVectorArray = 19
kMFnDataStringArray = 20
kMFnDataMatrixArray = 21
kMFnCompoundAttribute = 22
kMFnNumericInt64 = 23
kMFnNumericLast = 24
kMFnNumeric2Double = 25
kMFnNumeric2Float = 26
kMFnNumeric2Int = 27
kMFnNumeric2Long = 28
kMFnNumeric2Short = 29
kMFnNumeric3Double = 30
kMFnNumeric3Float = 31
kMFnNumeric3Int = 32
kMFnNumeric3Long = 33
kMFnNumeric3Short = 34
kMFnNumeric4Double = 35
kMFnMessageAttribute = 36


def mayaTypeFromZooType(zooType):
    if zooType == kMFnNumericBoolean:
        return om2.MFnNumericAttribute, om2.MFnNumericData.kBoolean
    elif zooType == kMFnNumericByte:
        return om2.MFnNumericAttribute, om2.MFnNumericData.kByte
    elif zooType == kMFnNumericShort:
        return om2.MFnNumericAttribute, om2.MFnNumericData.kShort
    elif zooType == kMFnNumericInt:
        return om2.MFnNumericAttribute, om2.MFnNumericData.kInt
    elif zooType == kMFnNumericLong:
        return om2.MFnNumericAttribute, om2.MFnNumericData.kLong
    elif zooType == kMFnNumericDouble:
        return om2.MFnNumericAttribute, om2.MFnNumericData.kDouble
    elif zooType == kMFnNumericFloat:
        return om2.MFnNumericAttribute, om2.MFnNumericData.kFloat
    elif zooType == kMFnNumericAddr:
        return om2.MFnNumericAttribute, om2.MFnNumericData.kAddr
    elif zooType == kMFnNumericChar:
        return om2.MFnNumericAttribute, om2.MFnNumericData.kChar
    elif zooType == kMFnNumeric2Double:
        return om2.MFnNumericAttribute, om2.MFnNumericData.k2Double
    elif zooType == kMFnNumeric2Float:
        return om2.MFnNumericAttribute, om2.MFnNumericData.k2Float
    elif zooType == kMFnNumeric2Int:
        return om2.MFnNumericAttribute, om2.MFnNumericData.k2Int
    elif zooType == kMFnNumeric2Long:
        return om2.MFnNumericAttribute, om2.MFnNumericData.k2Long
    elif zooType == kMFnNumeric2Short:
        return om2.MFnNumericAttribute, om2.MFnNumericData.k2Short
    elif zooType == kMFnNumeric3Double:
        return om2.MFnNumericAttribute, om2.MFnNumericData.k3Double
    elif zooType == kMFnNumeric3Float:
        return om2.MFnNumericAttribute, om2.MFnNumericData.k3Float
    elif zooType == kMFnNumeric3Int:
        return om2.MFnNumericAttribute, om2.MFnNumericData.k3Int
    elif zooType == kMFnNumeric3Long:
        return om2.MFnNumericAttribute, om2.MFnNumericData.k3Long
    elif zooType == kMFnNumeric3Short:
        return om2.MFnNumericAttribute, om2.MFnNumericData.k3Short
    elif zooType == kMFnNumeric4Double:
        return om2.MFnNumericAttribute, om2.MFnNumericData.k4Double

    if zooType == kMFnUnitAttributeDistance:
        return om2.MFnUnitAttribute, om2.MFnUnitAttribute.kDistance
    elif zooType == kMFnUnitAttributeAngle:
        return om2.MFnUnitAttribute, om2.MFnUnitAttribute.kAngle
    elif zooType == kMFnUnitAttributeTime:
        return om2.MFnUnitAttribute, om2.MFnUnitAttribute.kTime
    elif zooType == kMFnkEnumAttribute:
        return om2.MFnEnumAttribute, om2.MFn.kEnumAttribute

    if zooType == kMFnDataString:
        return om2.MFnTypedAttribute, om2.MFnData.kString
    elif zooType == kMFnDataMatrix:
        return om2.MFnTypedAttribute,om2.MFnData.kMatrix
    elif zooType == kMFnDataFloatArray:
        return om2.MFnTypedAttribute,om2.MFnData.kFloatArray
    elif zooType == kMFnDataDoubleArray:
        return om2.MFnTypedAttribute,om2.MFnData.kDoubleArray
    elif zooType == kMFnDataIntArray:
        return om2.MFnTypedAttribute,om2.MFnData.kIntArray
    elif zooType == kMFnDataPointArray:
        return om2.MFnTypedAttribute,om2.MFnData.kPointArray
    elif zooType == kMFnDataVectorArray:
        return om2.MFnTypedAttribute,om2.MFnData.kVectorArray
    elif zooType == kMFnDataStringArray:
        return om2.MFnTypedAttribute,om2.MFnData.kStringArray
    elif zooType == kMFnDataMatrixArray:
        return om2.MFnTypedAttribute,om2.MFnData.kMatrixArray

    elif zooType == kMFnMessageAttribute:
        return om2.MFnMessageAttribute, om2.MFn.kMessageAttribute
    return None, None
