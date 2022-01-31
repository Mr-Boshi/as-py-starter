      Subroutine neomean(imp, No1, No2, NoNz, neoKey)
c Calculation of Density mean Dneo and Vneo
c No1    - number of WORK to write Dneo
c No2    - number of WORK to write Vneo
c imp    - number of impurity to calculate for
c NoNz   - index of WORK where impurity density starts (SAME AS IN AS_STRAHL4!!!!) 
c neoKey - Flag to store neoclass. coeffs to WORK

      implicit none
      include 'strahl_config.inc'
      include 'elem_config.inc'
      include 'strahl_common.inc'
      include 'radiation_common.inc'
      include '../pec/emissivity.dimensions'
      include 'for/parameter.inc'
      include 'for/const.inc'
      include 'status2.inc'
      include 'for/outcmn.inc'
      common/as1/ rr,ir,nion,nelem
      !common/as5/v_neo,d_neo,rni,rne
      common /rhov/rhovol
      integer i, No, No1, No2, NoNz, imp, j1, j2, id, neoKey
      integer ir, nelem, nion(NELMAX)
      real*8  mDne(NRD), mVne(NRD), rr(RAP), sumN(NRD)!, rNE(RAP)!,rni(RAP),
      ! real*8  v_neo(RAP),d_neo(RAP)
      real*8  rhovol(NRD), nz(NRD), snz(NRD)

      do i=1,NAB
        id=0

c       Shifting id to the first ion of selected impurity
        if(imp.gt.1)then
          do j1=1,imp-1
            id=id+nion(j1)
          enddo
        endif

        if(neoKey.eq.1)then
          mDne(i)=0.d0
          mVne(i)=0.d0
          sumN(i)=0.d0
          
          do j2=1,nion(imp)
            mDne(i)=mDne(i)+WORK(i,NoNz+id+j2)*WORK(i,NoNz+451+id+j2)
            mVne(i)=mVne(i)+WORK(i,NoNz+id+j2)*WORK(i,NoNz+601+id+j2)
            sumN(i)=sumN(i)+WORK(i,NoNz+id+j2)
          enddo
          
          WORK(i,No1)=mDne(i)/sumN(i)
          WORK(i,No2)=mVne(i)/sumN(i)
        
        else
          WORK(i,No1)=0.
          WORK(i,No2)=0.
        endif
 
      enddo


      END ! subroutin
