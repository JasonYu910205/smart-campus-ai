import asyncio
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, select

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import (
    DeliveryRecord,
    Device,
    InspectionRecord,
    MaintenanceOrder,
    Product,
    PurchaseOrder,
    Supplier,
)

DEVICES = [
    (
        "DEV-PD-001",
        "3号宿舍楼低压配电箱",
        "配电箱",
        "3号宿舍楼一层配电间",
        "正泰电气",
        "XL-21",
        "warning",
    ),
    (
        "DEV-CF-A03",
        "第一食堂冷藏柜 A03",
        "冷藏柜",
        "第一食堂后厨冷藏区",
        "海尔商用冷链",
        "SL-1020C",
        "maintenance",
    ),
    ("DEV-DS-002", "第二食堂消毒柜", "消毒柜", "第二食堂餐具间", "康宝", "RTP700A", "online"),
    (
        "DEV-FC-001",
        "图书馆消防控制器",
        "消防设备",
        "图书馆消防控制室",
        "海湾安全",
        "JB-QB-GST5000",
        "online",
    ),
    ("DEV-EL-001", "行政楼 1 号电梯", "电梯", "行政楼东侧", "上海三菱", "LEHY-III", "online"),
    ("DEV-AC-007", "东门人脸门禁", "门禁", "校园东门", "海康威视", "DS-K1T671", "offline"),
    ("DEV-WM-012", "体育馆智能水表", "水表", "体育馆地下设备间", "宁波水表", "LXSY-50", "online"),
    (
        "DEV-GS-003",
        "第一食堂燃气报警器",
        "燃气设备",
        "第一食堂燃气间",
        "汉威科技",
        "KB-6010",
        "online",
    ),
    ("DEV-EF-004", "第二食堂排风机", "排风设备", "第二食堂屋顶", "绿岛风", "DPT20-55", "warning"),
    (
        "DEV-EM-021",
        "实验楼三相智能电表",
        "电表",
        "实验楼 B 区配电井",
        "威胜信息",
        "DTSD341",
        "online",
    ),
]
SUPPLIERS = [
    ("SUP-001", "华辰校园餐饮供应链有限公司", "A", "active"),
    ("SUP-002", "绿禾生鲜配送有限公司", "A", "active"),
    ("SUP-003", "安康冷链食品有限公司", "B", "active"),
    ("SUP-004", "启明校园设备服务有限公司", "B", "active"),
    ("SUP-005", "丰源粮油商贸有限公司", "A", "active"),
]
PRODUCTS = [
    ("PRD-001", "鲜牛肉", "肉类", "千克"),
    ("PRD-002", "冷鲜猪肉", "肉类", "千克"),
    ("PRD-003", "鸡蛋", "禽蛋", "箱"),
    ("PRD-004", "大米", "粮油", "袋"),
    ("PRD-005", "一级大豆油", "粮油", "桶"),
    ("PRD-006", "西红柿", "蔬菜", "千克"),
    ("PRD-007", "青菜", "蔬菜", "千克"),
    ("PRD-008", "纯牛奶", "乳制品", "箱"),
    ("PRD-009", "面粉", "粮油", "袋"),
    ("PRD-010", "冷冻鸡胸肉", "肉类", "千克"),
]


async def seed() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    async with SessionLocal() as session:
        if (await session.scalar(select(func.count()).select_from(Device))) or 0:
            return
        now = datetime.now(UTC)
        devices = [
            Device(
                device_code=x[0],
                device_name=x[1],
                device_type=x[2],
                location=x[3],
                manufacturer=x[4],
                model=x[5],
                status=x[6],
            )
            for x in DEVICES
        ]
        suppliers = [
            Supplier(supplier_code=x[0], supplier_name=x[1], level=x[2], status=x[3])
            for x in SUPPLIERS
        ]
        products = [
            Product(product_code=x[0], product_name=x[1], category=x[2], unit=x[3])
            for x in PRODUCTS
        ]
        session.add_all(devices)
        session.add_all(suppliers)
        session.add_all(products)
        await session.flush()
        inspectors = ["张伟", "李娜", "王强", "陈晨"]
        session.add_all(
            [
                InspectionRecord(
                    device_id=devices[i % 10].id,
                    inspector=inspectors[i % 4],
                    inspection_result="abnormal" if i in {2, 7, 15} else "normal",
                    description="发现运行参数异常，已通知值班人员"
                    if i in {2, 7, 15}
                    else "设备外观及运行参数正常",
                    inspected_at=now - timedelta(hours=i * 7),
                )
                for i in range(20)
            ]
        )
        faults = [
            (1, "E03", "三相电压不平衡", "in_progress", None),
            (2, "E03", "冷藏温度高于设定值", "pending", None),
            (2, "E03", "压缩机过热保护", "completed", "清洁冷凝器并补充制冷剂"),
            (6, "NET-01", "门禁网络离线", "pending", None),
            (9, "VIB-02", "排风机振动偏高", "in_progress", None),
            (5, "DR-11", "电梯门机异响", "completed", "调整门机皮带张力"),
            (4, "BAT-01", "备用电池容量不足", "completed", "更换控制器备用电池"),
            (8, "GAS-02", "传感器漂移", "completed", "重新标定传感器"),
            (7, "PULSE-01", "脉冲采集间歇中断", "completed", "紧固信号端子"),
            (3, "TEMP-02", "加热温度上升缓慢", "completed", "更换加热管"),
        ]
        session.add_all(
            [
                MaintenanceOrder(
                    device_id=devices[d - 1].id,
                    fault_code=c,
                    fault_description=f,
                    status=s,
                    resolution=r,
                    created_at=now - timedelta(days=i * 9 + 1),
                    completed_at=(now - timedelta(days=i * 9)) if s == "completed" else None,
                )
                for i, (d, c, f, s, r) in enumerate(faults)
            ]
        )
        orders = []
        for i in range(20):
            quantity = Decimal(str(50 + i * 5))
            price = Decimal(str(42 + (i % 6) * 1.8))
            order = PurchaseOrder(
                supplier_id=suppliers[i % 5].id,
                product_id=products[i % 10].id,
                quantity=quantity,
                unit_price=price,
                total_amount=quantity * price,
                purchased_at=now - timedelta(days=i * 3),
            )
            orders.append(order)
        session.add_all(orders)
        await session.flush()
        session.add_all(
            [
                DeliveryRecord(
                    supplier_id=orders[i].supplier_id,
                    purchase_order_id=orders[i].id,
                    expected_at=orders[i].purchased_at + timedelta(days=2),
                    delivered_at=orders[i].purchased_at
                    + timedelta(days=3 if i in {2, 5, 8} else 2),
                    status="delayed" if i in {2, 5, 8} else "delivered",
                )
                for i in range(10)
            ]
        )
        await session.commit()
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
