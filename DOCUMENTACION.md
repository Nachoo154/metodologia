# Documentación Trabajo Práctico Metodología

## Grupo 8

### Integrantes

- Correa, Damián.
- Ortiz, Ignacio.
- Servetti, Emilio.
- Zárate, Lautaro.

## Resumen de cambios por sprint

### Sprint 1

- **Registrar cliente:** se implementó la página de registro con las validaciones necesarias para los campos obligatorios y los formatos correctos.
- **Inicio de sesión:** se implementó la página de inicio de sesión con email y contraseña para usuarios regulares (no administradores).
- **Visualización de productos:** se creó una *landing page* que muestra los productos con su imagen, nombre y precio.
- **Panel de administrador:** se creó un panel de administración accesible únicamente a través de un *login* para administradores.
- **Administración de productos:** se agregaron formularios para la creación y edición de productos dentro del panel de administración.

### Sprint 2

- **Botón para agregar al carrito:** se incorporó en cada producto mostrado en la *landing page*.
- **Carrito de compras:** se agregó la página del carrito, que muestra cada producto con su información, su cantidad, un *input* para modificarla y un botón para eliminarlo del carrito.
- **Panel de vendedor:** se agregó un panel disponible únicamente para los usuarios con rol "vendedor".
- **Tabla de stocks:** se incorporó al panel de vendedor, con un *input* que permite modificar el stock de cada producto.
- **Página de finalización de compra:** se agregó un botón en el carrito que redirige a la página de finalización de compra. Allí se muestra un resumen de la operación y, al presionar el botón de finalizar, la compra se guarda con estado "pendiente" y se actualiza el stock de los productos afectados.

### Sprint 3

- **Reporte de stock mínimo:** se agregó una pantalla al panel de administrador que muestra los productos por debajo del stock mínimo (configurable). Cada producto cuenta con un botón para modificar su stock y, además, se incluye un botón para descargar el reporte de stock en formato *CSV*.
- **Reporte de productos más vendidos:** se agregó un botón en el panel de vendedor para generar un reporte con el ranking de los productos más vendidos y su cantidad vendida, en formato *CSV*.
- **Creación de cupones de descuento:** se agregó una página al panel de vendedor para crear, activar y desactivar cupones de descuento.
- **Uso de cupones de descuento:** los usuarios pueden aplicar cupones de descuento en sus compras, siempre que estén activos y se ingrese el código correcto.
- **Importación masiva de productos:** se agregó una alternativa de importación masiva de productos para administradores, mediante un archivo en formato *JSON*.

## Detalle de Historias de Usuario

### Sprint 1

#### HU 1 – Registrar cliente

**Descripción:** Como cliente, quiero poder crear una cuenta ingresando mi email, contraseña y nombre de usuario como datos mínimos, para poder gestionar mis compras y almacenar información adicional como métodos de pago y direcciones de envío.

**Criterios de aceptación:**

- El sistema debe exigir email, contraseña y nombre de usuario como campos obligatorios.
- La contraseña debe cumplir con criterios de seguridad mínimos.
- El sistema debe validar que el formato del email sea correcto.
- El usuario debe poder añadir y editar métodos de pago en su perfil.
- El usuario debe poder gestionar múltiples direcciones de envío.

**Pruebas de usuario:**

- Introducir un email con formato inválido → falla.
- Registrar un usuario omitiendo el campo de contraseña → falla.
- Registrar un usuario con todos los datos válidos → pasa.
- Almacenar un nuevo método de pago → pasa.
- Almacenar una dirección de envío → pasa.
- Registrar un usuario con un nombre de usuario ya existente → falla.

**Story points:** 3.

#### HU 5 – Visualizar productos

**Descripción:** Como cliente, quiero visualizar el listado de productos disponibles para poder consultar su información antes de realizar una compra.

**Criterios de aceptación:**

- El sistema debe mostrar un listado con los productos disponibles.
- Cada producto debe mostrar su nombre, precio e imagen.
- Si no hay productos cargados, se debe mostrar un mensaje informativo.
- Los productos deben cargarse desde la base de datos.
- La página debe permanecer accesible aunque el listado esté vacío.

**Pruebas de usuario:**

- Ver el listado de productos → pasa.
- Ver los datos de un producto específico → pasa.
- Acceder a un producto cuyo `id` no existe → falla con error 404.

**Story points:** 2.

#### HU 6 – Crear productos

**Descripción:** Como administrador, quiero crear productos ingresando sus datos obligatorios y una imagen, para que el producto quede registrado en el sistema.

**Criterios de aceptación:**

- Permitir el ingreso de los datos del producto.
- Validar que todos los campos obligatorios estén completos.
- No permitir campos vacíos.
- No permitir crear un producto sin imagen.
- Guardar el producto en la base de datos.
- Mostrar un mensaje de confirmación al crear el producto.
- El producto creado debe aparecer en el listado.

**Pruebas de usuario:**

- Crear un producto con campos vacíos → falla.
- Crear un producto sin imagen → falla.
- Crear un producto con datos inválidos → falla.
- Crear un producto con datos válidos → pasa.
- Recibir el mensaje de confirmación tras la creación → pasa.
- Verificar que el producto aparezca en el listado → pasa.

**Story points:** 4.

### Sprint 2

#### HU 2 – Carrito de compras

**Descripción:** Como cliente, quiero disponer de un carrito donde guardar los productos que deseo comprar, para poder visualizarlos posteriormente junto con su información y el precio total.

**Criterios de aceptación:**

- El sistema debe permitir agregar productos desde el catálogo al carrito.
- El usuario debe poder eliminar artículos individuales del carrito.
- El carrito debe mostrar el nombre, el precio unitario y la cantidad de cada producto añadido.
- El sistema debe realizar el cálculo automático del monto total sumando todos los artículos.
- El carrito debe estar vinculado a la cuenta del cliente (HU 1).

**Pruebas de usuario:**

- Agregar un producto al carrito y comprobar que aparece en la lista → pasa.
- Eliminar un producto y verificar que desaparece de la visualización → pasa.
- Visualizar los datos de los productos (nombre, precio, cantidad) → pasa.
- Comprobar que el precio total se calcula correctamente al sumar varios ítems → pasa.

**Story points:** 3.

#### HU 3 – Confirmar pedido con pago contra entrega

**Descripción:** Como cliente, quiero poder seleccionar la opción de pago contra entrega para pagar mis productos al momento de recibirlos, generando confianza en mi proceso de compra.

**Criterios de aceptación:**

- El sistema debe permitir elegir "Pago contra entrega" en las opciones de *checkout*.
- Se debe validar que el cliente haya ingresado una dirección de entrega válida.
- El pedido debe registrarse con el estado inicial "Pendiente de pago".
- El usuario debe poder confirmar la ubicación exacta de entrega antes de finalizar la compra.
- El estado debe actualizarse a "Pagado" una vez que se confirme la recepción física.

**Pruebas de usuario:**

- Confirmar un pedido seleccionando pago contra entrega → pasa.
- Verificar que el pedido se registre como "Pendiente de pago" → pasa.
- Cambiar el estado del pedido a "Pagado" tras recibir el producto → pasa.
- Confirmar la compra sin haber definido una dirección de entrega → falla.
- Seleccionar la ubicación de entrega antes de la confirmación → pasa.
- Seleccionar pago contra entrega en zonas sin cobertura → falla.

**Story points:** 5.

#### HU 4 – Visualizar el estado del pedido

**Descripción:** Como vendedor, quiero visualizar el estado de los pedidos asignados para coordinar las entregas pendientes y verificar los cobros realizados bajo la modalidad contra entrega.

**Criterios de aceptación:**

- El sistema debe mostrar un listado de pedidos con su estado actual (Pendiente, Pagado, Entregado).
- El vendedor debe poder filtrar los pedidos por dirección o zona de entrega.
- La vista debe permitir ver el detalle de contacto y los productos de cada pedido.
- El sistema debe permitir al vendedor marcar un pedido como "Entregado/Pagado" en tiempo real.
- La interfaz debe ser accesible desde dispositivos móviles para facilitar la consulta en ruta.

**Pruebas de usuario:**

- Acceder al listado de pedidos asignados al vendedor → pasa.
- Filtrar la lista por pedidos en estado "Pendiente de pago" → pasa.
- Visualizar la ubicación de entrega de un pedido específico → pasa.
- Actualizar el estado a "Pagado" tras una entrega exitosa → pasa.
- Intentar ver pedidos de otro vendedor sin los permisos correspondientes → falla.
- Probar el funcionamiento del listado sin conexión a internet → falla.

**Story points:** 5.

### Sprint 3

#### HU 9 – Importación masiva de productos

**Descripción:** Como administrador de productos, quiero cargar productos masivamente desde un archivo (CSV o XLS) para agilizar la actualización del catálogo.

**Criterios de aceptación:**

- Debe permitir cargar archivos en formato CSV o XLS.
- El sistema debe importar correctamente los productos del archivo.
- Si un producto ya existe, se deben actualizar sus datos.
- El sistema debe validar que el formato del archivo sea correcto.
- Debe validar que los datos obligatorios estén presentes.
- La importación debe realizarse de forma completa y consistente.
- Solo los usuarios con rol "administrador" pueden realizar la importación.

**Pruebas de usuario:**

- Cargar un archivo válido y verificar la importación correcta → pasa.
- Actualizar productos ya existentes → pasa.
- Detectar productos nuevos → pasa.
- Cargar un archivo con formato incorrecto → falla.
- Cargar datos incompletos → falla.
- Verificar que la importación se realiza completamente → pasa.
- Importar productos sin permisos de administrador → falla.

**Story points:** 4.

#### HU 11 – Generar cupón de descuento

**Descripción:** Como administrador, quiero generar cupones de descuento para poder ofrecer promociones y beneficios a los clientes.

**Criterios de aceptación:**

- Permitir la creación de un nuevo cupón de descuento.
- Permitir configurar el código del cupón.
- Permitir definir el porcentaje o monto de descuento.
- Permitir configurar la fecha de vigencia del cupón.
- Validar los datos obligatorios.
- Almacenar el cupón generado.
- Mostrar una confirmación tras la creación exitosa.

**Pruebas de usuario:**

- Crear un cupón válido → pasa.
- Crear un cupón sin código → falla.
- Crear un cupón sin descuento definido → falla.
- Configurar la vigencia correctamente → pasa.
- Verificar el guardado correcto del cupón → pasa.
- Verificar la confirmación de creación → pasa.

**Story points:** 4.

#### HU 12 – Agregar cupón de descuento a pedido

**Descripción:** Como cliente, quiero aplicar un cupón de descuento a mi pedido para obtener una reducción en el importe total de la compra.

**Criterios de aceptación:**

- Permitir el ingreso del código del cupón.
- Validar la existencia del cupón ingresado.
- Validar la vigencia del cupón.
- Aplicar el descuento de forma automática.
- Actualizar el total del pedido tras aplicar el cupón.
- Mostrar un mensaje de éxito al aplicar el cupón.
- Mostrar un mensaje de error ante un cupón inválido o vencido.

**Pruebas de usuario:**

- Aplicar un cupón válido → pasa.
- Aplicar un cupón inexistente → falla.
- Aplicar un cupón vencido → falla.
- Verificar la actualización correcta del total → pasa.
- Mostrar el mensaje de éxito tras aplicar el cupón → pasa.
- Mostrar el mensaje de error ante un cupón inválido → pasa.

**Story points:** 5.

#### HU 13 – Generar reporte de stock mínimo

**Descripción:** Como vendedor, quiero generar un reporte de productos con stock mínimo para identificar los productos que requieren reposición.

**Criterios de aceptación:**

- Consultar los productos según el stock mínimo configurado.
- Comparar el stock actual de cada producto con el stock mínimo.
- Incluir en el reporte los productos con stock menor o igual al mínimo establecido.
- Generar el reporte en pantalla.
- Visualizar la cantidad actual y la cantidad mínima requerida de cada producto.
- Permitir exportar el reporte.
- Mostrar una confirmación de generación exitosa.

**Pruebas de usuario:**

- Generar el reporte con productos en stock mínimo → pasa.
- Generar el reporte sin productos en stock mínimo → pasa.
- Visualizar las cantidades correctas → pasa.
- Exportar el reporte → pasa.
- Verificar la confirmación de generación → pasa.
- Detectar datos inconsistentes en el reporte → falla.

**Story points:** 4.

#### HU 14 – Generar reporte de productos más vendidos

**Descripción:** Como vendedor, quiero generar un reporte con los productos más vendidos para identificar cuáles tienen mayor demanda y tomar decisiones comerciales informadas (reposición, promociones, etc.).

**Criterios de aceptación:**

- Consultar las ventas registradas en el sistema.
- Calcular la cantidad total vendida por producto sumando todas las ventas confirmadas.
- Ordenar los productos por cantidad vendida en forma descendente.
- Limitar el ranking a los primeros productos con mayor volumen de ventas.
- Incluir en el reporte el nombre del producto y la cantidad total vendida.
- Permitir exportar el reporte.
- Mostrar un mensaje informativo cuando no existan ventas registradas.
- Solo los usuarios con rol "vendedor" pueden generar el reporte.

**Pruebas de usuario:**

- Generar el reporte con ventas registradas → pasa.
- Generar el reporte sin ventas registradas y verificar el mensaje informativo → pasa.
- Verificar el orden descendente por cantidad vendida → pasa.
- Verificar que las cantidades mostradas coinciden con las ventas reales → pasa.
- Exportar el reporte → pasa.
- Intentar generar el reporte sin permisos de vendedor → falla.

**Story points:** 4.
