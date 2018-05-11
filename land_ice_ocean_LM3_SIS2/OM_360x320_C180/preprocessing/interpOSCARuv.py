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
zi[0] = 0.0
zi[1:] = -30.0
nk=1 

zb =np.zeros((nk+1,S.grid.jm,S.grid.im))
for k in range(0,nk+1):
  zb[k,:]=zi[k]
  zb[k,:,:] = np.maximum( -S.grid.D, zb[k] )

for n in np.arange(0,293):
   O=state('/home/atw/data/currents/oscar/v2009/oscar_monthly_janstart.nc',fields=['u','v'],time_indices=np.arange(n,n+1),default_calendar='noleap',z_orientation=-1)
   O.grid.cyclic_x=True
   O.rename_field('u','uo')
   O.rename_field('v','vo')
   OM=O.horiz_interp('uo',target=S.grid,method='bilinear')
   OM=O.horiz_interp('vo',target=S.grid,method='bilinear',PrevState=OM)
   OM.adjust_thickness('uo')
   OM.adjust_thickness('vo')
   OM.fill_interior('uo',smooth=True,num_pass=10000)
   OM.fill_interior('vo',smooth=True,num_pass=10000)

   if n==0:
      OM.write_nc('OSCAR_uv_monthly.nc',['uo','vo'],append=False,write_interface_positions=True)
   else:
      OM.write_nc('OSCAR_uv_monthly.nc',['uo','vo'],append=True,write_interface_positions=True)
