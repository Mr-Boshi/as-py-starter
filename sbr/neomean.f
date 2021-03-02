      Subroutine neomean(imp, No1, No2)
c Calculation of Density mean Dneo and Vneo
c No1 - number of WORK to write Dneo
c No2 - number of WORK to write Vneo
c imp -- number of impurity to calculate for

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
      integer i, No, No1, No2, imp, j1, j2, id
      integer ir, nelem, nion(NELMAX)
      real*8  mDne(NRD), mVne(NRD), rr(RAP), sumN(NRD)!, rNE(RAP)!,rni(RAP),
      ! real*8  v_neo(RAP),d_neo(RAP)
      real*8  rhovol(NRD), nz(NRD), snz(NRD)

      do i=1,NAB
        mDne(i)=0.d0
        mVne(i)=0.d0
        sumN(i)=0.d0
        id=0
        if(imp.gt.1)then
          do j1=1,imp-1
            id=id+nion(j1)
          enddo
        endif

        do j2=1,nion(imp)
          mDne(i)=mDne(i)+WORK(i,300+id+j2)*WORK(i,750+id+j2)
          mVne(i)=mVne(i)+WORK(i,300+id+j2)*WORK(i,900+id+j2)
          sumN(i)=sumN(i)+WORK(i,300+id+j2)
        enddo

        WORK(i,No1)=mDne(i)/sumN(i)
        WORK(i,No2)=mVne(i)/sumN(i)

      enddo


      END ! subroutin
