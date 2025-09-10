Nombre: MicroServicios

Integrantes: 
    - Felipe Ferrada
    - Laura Leiva

Descripción:
    Una productora local nos ha solicitado una aplicación sencilla para gestionar las entradas de sus micro-eventos.
    Nos piden algo práctico y funcional que les permita cargar eventos, vender y devolver entradas. 
    Poder ver un resumen claro de lo que viene y de lo que ya está agotado. 
    La aplicación debe ser simple de operar y estar protegida por un inicio de sesión básico.

Instrucciones para ejecutar (idealmente Linux)
    - Clonar el repositorio 
        https://github.com/INF331-PruebasSw/MicroServicios.git
        cd ubicacion-del-repositorio
    - Crear y activar un entorno virtual
        python -m venv venv
        source venv/bin/activate
    - Instalar dependencias
        pip install -r requirements.txt
    - Ejecutar la aplicación
        flask run

Como usar:
    - Crear Usuario
    - Inicia sesión con tu usuario registrado.
    - Desde el panel principal puedes:
        Crear, editar y eliminar eventos.
        Registrar ventas o devoluciones de entradas.
        Consultar reportes con totales y eventos agotados.
        Usa los filtros para buscar eventos por título o categoría.

Cómo contribuir:
    - Haz un fork del repositorio.
    - Crea una nueva rama para tu funcionalidad:
        git checkout -b feature/nueva-funcionalidad
    - Realiza tus cambios y haz commit:
        git commit -m "Agrega nueva funcionalidad"
    - Haz push a tu rama:
        git push origin feature/nueva-funcionalidad
    - Abre un Pull Request y solicita revisión.

Licencia:
    - Este proyecto se distribuye bajo la licencia MIT.