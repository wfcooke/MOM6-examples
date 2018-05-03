#!/bin/csh 

module load fre/bronx-12


ln -s ../ocean_hgrid.nc .
ln -s ../topog.nc .
make_hgrid --grid_type gnomonic_ed --nlon 768  --grid_name C384_grid
make_solo_mosaic --num_tiles 6 --dir . --mosaic_name C384_mosaic --tile_file C384_grid.tile1.nc,C384_grid.tile2.nc,C384_grid.tile3.nc,C384_grid.tile4.nc,C384_grid.tile5.nc,C384_grid.tile6.nc
make_solo_mosaic --num_tiles 1 --dir ./ --mosaic_name ocean_mosaic --tile_file ocean_hgrid.nc --periodx 360.
make_coupler_mosaic --atmos_mosaic C384_mosaic.nc --ocean_mosaic ocean_mosaic.nc --ocean_topog topog.nc --mosaic_name grid_spec
#rm -f hydrology*.nc

#./run.cr_simple_hydrog.csh -f 0. -t 1.e-5 -m ../grid_spec.nc -o . -c compile
#(mv work/*.nc .;foreach tile ( tile1 tile2 tile3 tile4 tile5 tile6 );mv hydrography.$tile.nc river_data.$tile.nc;end)
#(tar cvhf mosaic.tar C192_grid* C192_mosaic* lake_frac* land_mask* ocean_hgrid* ocean_mask* ocean_mosaic* river_data* topog* grid_spec.nc)
(tar cvhf mosaic.tar C384_grid* C384_mosaic* land_mask* ocean_hgrid* ocean_mask* ocean_mosaic* topog* grid_spec.nc)
#(mkdir quick_mosaic;cd quick_mosaic;make_quick_mosaic --mosaic_name grid_spec --input_mosaic ../grid_spec.nc)
#(cd quick_mosaic;ln -s ../C192_grid.tile*.nc .;ln -s ../C192_mosaic.nc .;ln -s ../lake_frac* .;ln -s ../river_data* .;ln -s ../topog.nc .)
#(cd quick_mosaic;tar chvf ../quick_mosaic.tar C192_grid* C192_mosaic* lake_frac* land_mask* ocean_mask* river_data* topog* atmos_mosaic* land_mosaic* grid_spec.nc)
