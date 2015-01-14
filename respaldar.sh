export FECHA=`date +%Y%m%d`
export NAME=${FECHA}
export DIR='/home/panaderia/pymeadmin/respaldos/'
cd $DIR
pg_dump -i -h localhost -p 5432 -U postgres -F c -b -v -f ${NAME}.backup admin0
return_code=$?
if [ $return_code -ne 0 ]
then
   echo 'Error en el backup. Compruebe: usuario y permisos'
else
   echo 'Backup realizado correctamente. Archivo' ${NAME}.backup
fi

