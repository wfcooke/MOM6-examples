#!/usr/bin/env python

from midas.rectgrid import *
import netCDF4 as nc
import numpy as np

sgrid=supergrid(file='ocean_hgrid.nc',cyclic_x=True,tripolar_n=True)
grid=quadmesh(supergrid=sgrid)
grid.lath=grid.y_T[:,grid.im/4]
grid.latq=grid.y_T_bounds[:,grid.im/4]
grid.D=nc.Dataset('topog.nc').variables['depth'][:]
grid.wet=np.zeros(grid.D.shape)
grid.wet[grid.D>0.]=1
S=state(grid=grid)

# Model vertical grid
#dz=nc.Dataset('../../../examples/ocean_SIS/OM4_025/INPUT/vgrid_75_2m.nc').variables['dz'][:]
#nk = dz.shape[0]
#zi=np.zeros(nk+1)
#zi[1:]=np.cumsum(-dz)
# Analysis vertical  grid
#zi=-nc.Dataset('../../../ice_ocean_SIS/OM4_025/INPUT/vgrid_75_2m.nc').variables['zw'][:]
zi=-nc.Dataset('../../../land_ice_ocean_LM3_SIS2/OM_360x320_C180/INPUT/vgrid_75_2m.nc').variables['zw'][:]
nk=zi.shape[0]-1

zb =np.zeros((nk+1,S.grid.jm,S.grid.im))
for k in range(0,nk+1):
  zb[k,:]=zi[k]
  zb[k,:,:] = np.maximum( -S.grid.D, zb[k] )

for n in np.arange(0,456):
   O=state('/archive/atw/data/ecmwf/era-interim/era_interim_monthly.nc',fields=['tau_x','tau_y','netflx','shflx','lhflx'],time_indices=np.arange(n,n+1),default_calendar='noleap',z_orientation=-1)
   O.grid.cyclic_x=True
   #O.rename_field('tau_x','taux')
   #O.rename_field('tau_y','tauy')
   OM=O.horiz_interp('tau_x',target=S.grid,method='bilinear')
   OM=O.horiz_interp("tau_y",target=S.grid,method='bilinear',PrevState=OM)
   OM=O.horiz_interp("netflx",target=S.grid,method='bilinear',PrevState=OM)
   OM=O.horiz_interp("shflx",target=S.grid,method='bilinear',PrevState=OM)
   OM=O.horiz_interp("lhflx",target=S.grid,method='bilinear',PrevState=OM)
   OM.mask_where('tau_x','grid.wet==0.')
   OM.mask_where('tau_y','grid.wet==0.')
   OM.mask_where('netflx','grid.wet==0.')
   OM.mask_where('shflx','grid.wet==0.')
   OM.mask_where('lhflx','grid.wet==0.')

   if n==0:
      OM.write_nc('ERA_oceanfluxes_monthly.nc',['tau_x','tau_y','netflx','shflx','lhflx'],append=False,write_interface_positions=True)
   else:
      OM.write_nc('ERA_oceanfluxes_monthly.nc',['tau_x','tau_y','netflx','shflx','lhflx'],append=True,write_interface_positions=True)
