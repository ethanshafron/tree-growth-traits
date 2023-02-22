BASEDIR="/Users/shafron/Desktop/thesis"
DATADIR="${BASEDIR}/data"
NEONDIR="${DATADIR}/neon"
TRAITSDIR="${DATADIR}/traits"
FILELISTDIR="${BASEDIR}/filelists"
CONFIGDIR="${BASEDIR}/configs"
MOSAIC_LIST=${FILELISTDIR}/chm_mosaic_list.txt

SCRIPTDIR="${BASEDIR}/scripts"
DOWNLOAD_NEON_SCRIPT="${SCRIPTDIR}/download_neon.py"

mkdir ${CONFIGDIR}
mkdir ${FILELISTDIR}
mkdir ${DATADIR}
mkdir ${NEONDIR}
mkdir ${TRAITSDIR}


echo "DOWNLOADING NEON CHM DATA..."
python ${DOWNLOAD_NEON_SCRIPT}
echo "NEON DATA DOWNLOADED TO ${NEONDIR}"

$(echo basename ${NEONDIR}/*CHM.tif ) | cut -d"_" -f1 -f2 | sort | uniq > ${MOSAIC_LIST} 

echo "GENERATING CHM MOSAICS..."
parallel python scripts/rio_merge.py --output ${NEONDIR}/{1}_mosaic.tif --inputs ${NEONDIR}/{1}*.tif :::: ${MOSAIC_LIST}
echo "CHM MOSAICING COMPLETED"











sampleraster.py -i crowns_intersect_good_filtered.geojson -o crowns_with_data.geojson chm13=data/neon/SJER_2013_mosiac.vrt

parallel gdalbuildvrt {1}_{2}_mosaic.vrt \$\(find {1} -name \"*_{2}\" \) ::: yosemite_20150602 yosemite_20140603 yosemite_20130612 ::: LMA Nitrogen NSC d13C



parallel gdal_merge.py -separate -o {1}_LMA_NSC_Nit_d13.tif \$\(find . -name \"{1}_*_mosaic.vrt\" \| sort \) ::: yosemite_20150602 yosemite_20140603 yosemite_20130612 
