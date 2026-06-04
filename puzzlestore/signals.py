from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Supply, Sale

@receiver(post_save, sender=Supply)
def update_stock_on_supply(sender, instance, created, **kwargs):
    if created:
        game = instance.game
        game.current_stock += instance.quantity
        game.save(update_fields=['current_stock'])

@receiver(post_delete, sender=Supply)
def update_stock_on_supply_delete(sender, instance, **kwargs):
    game = instance.game
    game.current_stock -= instance.quantity
    game.save(update_fields=['current_stock'])

@receiver(post_save, sender=Sale)
def update_stock_on_sale(sender, instance, created, **kwargs):
    if created:
        game = instance.game
        game.current_stock -= instance.quantity
        game.save(update_fields=['current_stock'])

@receiver(post_delete, sender=Sale)
def update_stock_on_sale_delete(sender, instance, **kwargs):
    game = instance.game
    game.current_stock += instance.quantity
    game.save(update_fields=['current_stock'])