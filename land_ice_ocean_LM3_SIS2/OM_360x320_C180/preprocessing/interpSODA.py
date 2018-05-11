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

for n in np.arange(0,1):
   #for n in np.arange(0,432):
   O=state('/archive/atw/data/oda/soda/v3.4.1/monthly/1_deg/soda_v3.4.1.nc',fields=['temp','salt','ssh','u','v'],time_indices=np.arange(n,n+1),default_calendar='noleap',z_orientation=-1)
   O.grid.cyclic_x=True
   O.rename_field('temp','ptemp')
   O.rename_field('u','uo')
   O.rename_field('v','vo')
   O.rename_field('salt','s')
   print(O.s[0,0,:,180])
   OM=O.horiz_interp('s',target=S.grid,method='bilinear')
   print(OM.s.shape,OM.s[0,0,:,180])
   OM=O.horiz_interp('ptemp',target=S.grid,method='bilinear',PrevState=OM)
   OM=O.horiz_interp('uo',target=S.grid,method='bilinear',PrevState=OM)
   OM=O.horiz_interp('vo',target=S.grid,method='bilinear',PrevState=OM)
   OM=O.horiz_interp('ssh',target=S.grid,method='bilinear',PrevState=OM)
   OM.adjust_thickness('ptemp')
   OM.adjust_thickness('s')
   print(OM.s[0,0,:,180])
   OM.adjust_thickness('vo')
   OM.adjust_thickness('vo')
   OM.fill_interior('s',smooth=False,num_pass=10000)
   print(OM.s[0,0,:,180])
   #OM.fill_interior('ptemp',smooth=True,num_pass=10000)
   #OM.fill_interior('uo',smooth=True,num_pass=10000)

   #OM.remap_ALE(fields=['ptemp','s','uo','vo'],z_bounds=zb,zbax_data=-zi,method='ppm_h4',bndy_extrapolation=False)
   #OM.rename_field('ptemp_remap','ptemp')
   #OM.rename_field('s_remap','s')
   #print(OM.s[0,0,:,180])
   #OM.rename_field('uo_remap','uo')
   #OM.rename_field('vo_remap','vo')
   OM.mask_where('ptemp','grid.wet==0.')
   OM.mask_where('s','grid.wet==0.')
   print(OM.s[0,0,:,180])
   OM.mask_where('uo','grid.wet==0.')
   OM.mask_where('vo','grid.wet==0.')
   OM.mask_where('ssh','grid.wet==0.')
   OM.ptemp=np.ma.masked_where(OM.var_dict['ptemp']['dz'][np.newaxis,:]<1.e-2, OM.ptemp)
   OM.s=np.ma.masked_where(OM.var_dict['ptemp']['dz'][np.newaxis,:]<1.e-2, OM.s)
   print(OM.s[0,0,:,180])
   OM.uo=np.ma.masked_where(OM.var_dict['uo']['dz'][np.newaxis,:]<1.e-2, OM.uo)
   OM.vo=np.ma.masked_where(OM.var_dict['s']['dz'][np.newaxis,:]<1.e-2, OM.vo)

   if n==0:
      OM.write_nc('SODA_ptemp_s_monthly.nc',['ptemp','s','uo','vo','ssh'],append=False,write_interface_positions=True)
   else:
      OM.write_nc('SODA_ptemp_s_monthly.nc',['ptemp','s','uo','vo','ssh'],append=True,write_interface_positions=True)
