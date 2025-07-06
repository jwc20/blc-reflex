import reflex as rx

config = rx.Config(
    app_name="blc_reflex",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ],
)