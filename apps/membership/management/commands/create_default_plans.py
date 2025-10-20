from django.core.management.base import BaseCommand
from apps.membership.models import MembershipPlan


class Command(BaseCommand):
    help = '创建默认会员套餐'

    def handle(self, *args, **options):
        plans = [
            {
                'name': '月度会员',
                'plan_type': 'monthly',
                'price': 19.9,
                'original_price': 29.9,
                'duration_days': 30,
                'description': '享受一个月的会员特权',
                'features': ['无限海报生成', '4K高清输出', '优先客服支持'],
                'poster_quota': -1,
                'max_image_size': '4K',
                'priority_generation': True,
                'sort_order': 1,
            },
            {
                'name': '季度会员',
                'plan_type': 'quarterly',
                'price': 49.9,
                'original_price': 89.7,
                'duration_days': 90,
                'description': '三个月会员，性价比之选',
                'features': ['无限海报生成', '4K高清输出', '优先客服支持', '专属模板'],
                'poster_quota': -1,
                'max_image_size': '4K',
                'priority_generation': True,
                'is_featured': True,
                'sort_order': 2,
            },
            {
                'name': '年度会员',
                'plan_type': 'yearly',
                'price': 168.0,
                'original_price': 358.8,
                'duration_days': 365,
                'description': '一年会员，超值享受',
                'features': ['无限海报生成', '8K超高清输出', '优先客服支持', '专属模板', 'API接口调用'],
                'poster_quota': -1,
                'max_image_size': '8K',
                'priority_generation': True,
                'sort_order': 3,
            }
        ]

        for plan_data in plans:
            plan, created = MembershipPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults=plan_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'成功创建套餐: {plan.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'套餐已存在: {plan.name}')
                )