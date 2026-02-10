# BigQuery Schema: `bigquery-public-data.thelook_ecommerce`

## orders
| Column       | Type      |
|-------------|-----------|
| order_id    | INTEGER   |
| user_id     | INTEGER   |
| status      | STRING    |
| gender      | STRING    |
| created_at  | TIMESTAMP |
| returned_at | TIMESTAMP |
| shipped_at  | TIMESTAMP |
| delivered_at| TIMESTAMP |
| num_of_item | INTEGER   |

## order_items
| Column             | Type      |
|-------------------|-----------|
| id                | INTEGER   |
| order_id          | INTEGER   |
| user_id           | INTEGER   |
| product_id        | INTEGER   |
| inventory_item_id | INTEGER   |
| status            | STRING    |
| created_at        | TIMESTAMP |
| shipped_at        | TIMESTAMP |
| delivered_at      | TIMESTAMP |
| returned_at       | TIMESTAMP |
| sale_price        | FLOAT     |

## products
| Column                 | Type    |
|-----------------------|---------|
| id                    | INTEGER |
| cost                  | FLOAT   |
| category              | STRING  |
| name                  | STRING  |
| brand                 | STRING  |
| retail_price          | FLOAT   |
| department            | STRING  |
| sku                   | STRING  |
| distribution_center_id| INTEGER |

## users (PII columns marked with *)
| Column          | Type      |
|----------------|-----------|
| id             | INTEGER   |
| first_name *   | STRING    |
| last_name *    | STRING    |
| email *        | STRING    |
| age            | INTEGER   |
| gender         | STRING    |
| state *        | STRING    |
| street_address*| STRING    |
| postal_code *  | STRING    |
| city *         | STRING    |
| country *      | STRING    |
| latitude       | FLOAT     |
| longitude      | FLOAT     |
| traffic_source | STRING    |
| created_at     | TIMESTAMP |
| user_geom      | GEOGRAPHY |

## Relationships
- `orders.user_id` -> `users.id`
- `order_items.order_id` -> `orders.order_id`
- `order_items.user_id` -> `users.id`
- `order_items.product_id` -> `products.id`
