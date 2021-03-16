      subroutine tostop

      implicit none
      include 'for/parameter.inc'
      include 'for/const.inc'
      include 'for/outcmn.inc'
      include 'for/status.inc'
      include	'for/timeoutput.inc'
      integer i,j,ier
      character filename*40
 
         filename='dat/dynam.dat'
                  ! print*,filename
         CALL OPENWT(11,filename,0,ier)
         write(11,'(17(A4,8X))')'Time',(NAMET(J),J=1,16)
         do I=1,LTOUT-1
            write(11,'(17(E11.5,1X))')TTOUT(I),(tout(I,J),J=1,16)
         enddo
         close(11)

         filename='dat/radial.dat'
                  ! print*,filename
         CALL OPENWT(13,filename,0,ier)
         write(13,'(8(A3,9X))')
     >    'Rad',
     >    'Prc',
     >    'Prx',
     >    'Van',
     >    'Dan',
     >    'Vnc',
     >    'Dnc',
     >    'n_W'
         do J=1,NA1
            write(13,'(8(E11.5,1X))')
     >      AMETR(J),
     >      CAR3(J),
     >      PRADX(J),
     >      CN(J),
     >      DN(J),
     >      CAR7(J)*1.e-4,
     >      CAR8(J)*1.e-2,
     >      CAR5(J)
         enddo
         close(13)
      
         ! print*,'Data saved in dynam.dat and radial.dat stored in /dat'


C          CALL OPENWT(12,'dat/flagfile',0,ier)
C          close(12)

      stop
      end
