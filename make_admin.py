# set_admin.py
import asyncio
from sqlalchemy import select, update
from database import async_session_maker
from models.user import User, UserRole

async def set_admin_user():
    """Простой скрипт для назначения администратора"""
    async with async_session_maker() as session:
        print("=" * 50)
        print("👑 НАЗНАЧЕНИЕ АДМИНИСТРАТОРА")
        print("=" * 50)
        
        try:
            # Получаем всех пользователей
            result = await session.execute(select(User))
            users = result.scalars().all()
            
            if not users:
                print("❌ В базе нет пользователей!")
                print("   Сначала зарегистрируйтесь через API")
                return
            
            print("\n📋 НАЙДЕННЫЕ ПОЛЬЗОВАТЕЛИ:")
            print("-" * 40)
            
            for i, user in enumerate(users, 1):
                role_icon = "👑" if user.role == UserRole.ADMIN else "👤"
                print(f"{i}. {role_icon} {user.nickname}")
                print(f"   Email: {user.email}")
                print(f"   Текущая роль: {user.role.value}")
                print(f"   ID: {user.id}")
                print()
            
            # Выбор пользователя
            try:
                choice = int(input("👉 Введите номер пользователя для назначения админом: "))
                
                if 1 <= choice <= len(users):
                    selected_user = users[choice - 1]
                    
                    # Проверяем текущую роль
                    if selected_user.role == UserRole.ADMIN:
                        print(f"\n⚠️  Пользователь {selected_user.nickname} УЖЕ администратор!")
                        demote = input("   Понизить до обычного пользователя? (y/n): ").lower() == 'y'
                        if demote:
                            selected_user.role = UserRole.USER
                            await session.commit()
                            print(f"✅ Пользователь {selected_user.nickname} теперь обычный пользователь")
                        else:
                            print("⏸️  Роль не изменена")
                    else:
                        # Назначаем админом
                        selected_user.role = UserRole.ADMIN
                        await session.commit()
                        print(f"\n🎉 ПОЛЬЗОВАТЕЛЬ НАЗНАЧЕН АДМИНИСТРАТОРОМ!")
                        print(f"   👑 {selected_user.nickname}")
                        print(f"   📧 {selected_user.email}")
                        print(f"   🔑 ID: {selected_user.id}")
                        
                        # Показываем подтверждение
                        await session.refresh(selected_user)
                        print(f"\n✅ Подтверждение: роль изменена на {selected_user.role.value}")
                else:
                    print("❌ Неверный номер пользователя")
                    
            except ValueError:
                print("❌ Пожалуйста, введите число")
            except KeyboardInterrupt:
                print("\n⏸️  Операция отменена пользователем")
                
        except Exception as e:
            print(f"❌ ОШИБКА: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(set_admin_user())