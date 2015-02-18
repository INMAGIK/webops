import ogr
import os
import tempfile
import datetime

from opsmanager.ops import BaseOp
from rest_framework import serializers
from rest_framework.exceptions import APIException


def make_intersection(InFile1,InFile2,outfile):

    with open(InFile1) as f1, open(InFile2) as f2:
        data1 = f1.read()
        data2 = f2.read()

        a = ogr.CreateGeometryFromJson(data1)
        b = ogr.CreateGeometryFromJson(data2)
        out = a.Intersection(b)
        geomcol =  ogr.Geometry(ogr.wkbGeometryCollection)
        geomcol.AddGeometry(out)
        json = geomcol.ExportToJson()

        with open(outfile, "wb") as f:
            f.write(json)





class IntersectionFilesSerializer(serializers.Serializer):

    in_file1 = serializers.FileField(help_text='Input file')
    in_file2 = serializers.FileField(help_text='Input file')




class IntersectionOp(BaseOp):

    op_name  = "Intersection"
    op_package = "geo"
    op_description = "Create intersection from two geojson"
    #parameters_serializer = IntersectionParamsSerializer
    files_serializer = IntersectionFilesSerializer




    def process(self, files, parameters):

        file1 = files.validated_data["in_file1"]
        file2 = files.validated_data["in_file2"]

        #get it on the tmp
        tmp_src1 = tempfile.NamedTemporaryFile(suffix=file1.name, delete=False)
        tmp_src1.write(file1.read())
        tmp_src1.close()

        tmp_src2 = tempfile.NamedTemporaryFile(suffix=file1.name, delete=False)
        tmp_src2.write(file2.read())
        tmp_src2.close()

        #get a tmp filename for dst
        tmp_dst=  tmp_src1.name + ".geojson"


        try:
          msg = make_intersection(tmp_src1.name, tmp_src2.name, tmp_dst)

        except Exception, e:
          print e
          raise APIException(detail=str(e))

        return { "filename" : tmp_dst }
