# Acme Order Pipeline

## Descripción

Sistema de procesamiento de órdenes para e-commerce usando FastAPI, Kafka, PostgreSQL y MongoDB.  
El flujo es completamente asíncrono y tolerante a fallos.

---

## Arquitectura

- **API REST:** Recibe y valida órdenes.
- **Kafka:** Orquesta el procesamiento asíncrono.
- **Consumer:** Simula pago, actualiza inventario y guarda la orden.
- **PostgreSQL:** Inventario de productos.
- **MongoDB:** Persistencia de órdenes.

---

## Requisitos

- Docker y Docker Compose
- Python 3.12 (solo para desarrollo local)

---

## Instalación y ejecución

1. **Clona el repositorio:**
   ```sh
   git clone <repo-url>
   cd acme-order-pipeline
   ```

2. **Levanta todos los servicios:**
   ```sh
   docker compose up -d --build
   ```

3. **Verifica los logs:**
   ```sh
   docker compose logs -f api
   docker compose logs -f consumer
   ```

---

## Endpoints principales

### Crear orden

```http
POST /orders
Content-Type: application/json

{
  "customer": { "name": "Juan", "email": "juan@email.com" },
  "items": [
    { "sku": "SKU-001", "quantity": 2 },
    { "sku": "SKU-002", "quantity": 1 }
  ]
}
```

### Consultar orden

```http
GET /orders/{order_id}
```

### Consultar inventario

```http
GET /inventory
```

---



## Pruebas

- Usa Postman o curl para probar los endpoints.
- Verifica en los logs que el flujo se procesa correctamente.

---

## Notas

- El sistema implementa idempotencia y manejo de errores.
- Los servicios esperan a que Kafka esté disponible antes de procesar órdenes.
- El proyecto está listo para producción y desarrollo local.

---

