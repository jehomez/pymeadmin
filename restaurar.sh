export FECHA=`date +%Y%m%d`
export NAME=${FECHA}
export DIR='/home/panaderia/pymeadmin/respaldos/'
cd $DIR
dropdb -h localhost -p 5432 -U postgres admin0
createdb -h localhost -p 5432 -U postgres admin0
pg_restore -i -h localhost -p 5432 -U postgres -d admin0 -v  ${NAME}.backup
if [ $return_code -ne 0 ]
then
   echo 'Error en la restauración. Compruebe: usuario y permisos'
else
   echo 'Restauración realizada correctamente. Archivo' ${NAME}.backup
fi
