import math

import numpy as np
import pandas as pd


class MetricProcessor:
    def calculate_main_metrics(self):
        profit_orders = [x['profit'] for x in self.closed_trades if x['profit'] > 0]
        loss_orders = [x['profit'] for x in self.closed_trades if x['profit'] <= 0]
        return {
            "full_deals_cnt": len(profit_orders + loss_orders),
            "full_deals_saldo": round(sum(profit_orders + loss_orders), 2),
            "profit_deals_cnt": len(profit_orders),
            "prodfit_deals_saldo": round(sum(profit_orders), 2),
            "loss_deals_cnt": len(loss_orders),
            "loss_deals_saldo": round(sum(loss_orders), 2),
        }

    def calculate_additional_metrics(self):
        if len(self.closed_trades) == 0:
            return None
        df_trades = pd.DataFrame(self.closed_trades)
        # 1. Временные метрики
        start_date = self.data.index[0]
        end_date = self.data.index[-1]
        duration = end_date - start_date
        total_days = duration.days
        exposure_time = (df_trades['close_time'] - df_trades['open_time']).sum().days / total_days * 100
        
        # 2. Метрики по капиталу
        df_trades['capital'] = self.initial_capital + df_trades['profit'].cumsum()
        final_capital = df_trades['capital'].iloc[-1]
        peak_capital = df_trades['capital'].max()
        return_percent = (final_capital - self.initial_capital) / self.initial_capital * 100
        buy_and_hold_return = (self.data['Close'].iloc[-1] - self.data['Close'].iloc[0]) / self.data['Close'].iloc[0] * 100
        
        # 3. Годовая доходность и волатильность
        if return_percent <= -100:
            annual_return = 0
        else:
            annual_return = ((1 + return_percent / 100) ** (365 / total_days) - 1) * 100
        annual_volatility = df_trades['profit'].std() * np.sqrt(252)

        # 4. Коэффициенты Шарпа, Сортино и Кальмара
        sharpe_ratio = annual_return / annual_volatility
        downside_returns = df_trades[df_trades['profit'] < 0]['profit']
        if downside_returns.std() == 0:
            sortino_ratio = 0
        else:
            sortino_ratio = annual_return / (downside_returns.std() * np.sqrt(252))
        calmar_ratio = annual_return / abs(df_trades['capital'].min() - peak_capital)

        # 5. Просадки
        df_trades['drawdown'] = peak_capital - df_trades['capital']
        max_drawdown = df_trades['drawdown'].max()
        avg_drawdown = df_trades['drawdown'].mean()
        max_drawdown_duration = (df_trades['drawdown'].idxmax() - df_trades['capital'].idxmax())
        avg_drawdown_duration = df_trades[df_trades['drawdown'] > 0].index.to_series().diff().mean()

        # 6. Метрики по сделкам
        num_trades = len(df_trades)
        win_rate = (df_trades['result'] == 'TP').sum() / num_trades * 100
        best_trade = df_trades['profit'].max()
        worst_trade = df_trades['profit'].min()
        avg_trade_volume = df_trades['profit'].mean()
        max_trade_duration = (df_trades['close_time'] - df_trades['open_time']).max().days
        avg_trade_duration = (df_trades['close_time'] - df_trades['open_time']).mean().days

        # 7. Фактор прибыли, ожидание, SQN
        profit_factor = df_trades[df_trades['profit'] > 0]['profit'].sum() / abs(df_trades[df_trades['profit'] < 0]['profit'].sum())
        expectation = df_trades['profit'].mean() / abs(df_trades['profit'].std()) * 100
        sqn = df_trades['profit'].mean() / df_trades['profit'].std() * np.sqrt(num_trades)
        report = {
            'start_date': str(start_date),
            'end_date': str(end_date),
            'duration': str(duration),
            'exposure_time': exposure_time,
            'final_capital': final_capital,
            'peak_capital': peak_capital,
            'return_percent': return_percent,
            'buy_and_hold_return': buy_and_hold_return,
            'annual_return': annual_return,
            'annual_volatility': annual_volatility,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'calmar_ratio': calmar_ratio,
            'max_drawdown': max_drawdown,
            'avg_drawdown': avg_drawdown,
            'max_drawdown_duration': max_drawdown_duration,
            'avg_drawdown_duration': avg_drawdown_duration,
            'num_trades': num_trades,
            'win_rate': win_rate,
            'best_trade': best_trade,
            'worst_trade': worst_trade,
            'avg_trade_volume': avg_trade_volume,
            'max_trade_duration': max_trade_duration,
            'avg_trade_duration': avg_trade_duration,
            'profit_factor': profit_factor,
            'expectation': expectation,
            'SQN': sqn
        }
        not_round_fields = {
            "start_date", "end_date", "duration", "max_drawdown_duration", "avg_drawdown_duration",
            "max_trade_duration", "avg_trade_duration"
        }
        for key in report:
            if str(report[key]) == "nan":
                report[key] = 0
            try:
                if not math.isfinite(report[key]):
                    report[key] = 0
            except Exception:
                pass
            if key not in not_round_fields:
                report[key] = round(report[key], 2)
        return report

    def analyze_trading_report(self, report):
        conclusions = []

        # Анализ прибыли и убытков
        if report["return_percent"] < 0:
            conclusions.append(f"Торговая стратегия показала отрицательный результат с возвратом {report['return_percent']:.2f}% за весь период.")
        else:
            conclusions.append(f"Торговая стратегия показала положительный результат с возвратом {report['return_percent']:.2f}% за весь период.")

        # Годовая доходность
        if report["annual_return"] > 0:
            conclusions.append(f"Годовая доходность составила {report['annual_return']:.2f}%.")
        else:
            conclusions.append("Годовая доходность отрицательная.")

        # Волатильность
        conclusions.append(f"Годовая волатильность составила {report['annual_volatility']:.2f}%.")

        # Коэффициенты Шарпа, Сортино, Кальмара
        if report["sharpe_ratio"] > 1:
            conclusions.append(f"Коэффициент Шарпа равен {report['sharpe_ratio']:.2f}, что указывает на хорошее соотношение доходности к риску.")
        else:
            conclusions.append(f"Коэффициент Шарпа равен {report['sharpe_ratio']:.2f}, что указывает на низкую доходность по сравнению с риском.")

        if report["sortino_ratio"] > 1:
            conclusions.append(f"Коэффициент Сортино равен {report['sortino_ratio']:.2f}, что указывает на хорошую доходность при управляемом риске.")
        else:
            conclusions.append(f"Коэффициент Сортино равен {report['sortino_ratio']:.2f}, что свидетельствует о высоких убытках по сравнению с ожидаемой доходностью.")

        if report["calmar_ratio"] > 1:
            conclusions.append(f"Коэффициент Кальмара равен {report['calmar_ratio']:.2f}, что указывает на благоприятное соотношение доходности к максимальной просадке.")
        else:
            conclusions.append(f"Коэффициент Кальмара равен {report['calmar_ratio']:.2f}, что указывает на значительные потери капитала.")
        # Максимальная и средняя просадки
        conclusions.append(f"Максимальная просадка составила {report['max_drawdown']:.2f}%, что может указывать на значительные потери капитала.")
        conclusions.append(f"Средняя просадка составила {report['avg_drawdown']:.2f}%.")
        # Фактор прибыли
        if report["profit_factor"] > 1:
            conclusions.append(f"Фактор прибыли составляет {report['profit_factor']:.2f}, что означает, что стратегия была прибыльной.")
        else:
            conclusions.append(f"Фактор прибыли составляет {report['profit_factor']:.2f}, что указывает на то, что стратегия была убыточной.")
        # Процент побед
        conclusions.append(f"Процент побед составил {report['win_rate']:.2f}%.")
        # Лучшие и худшие сделки
        conclusions.append(f"Лучшая сделка принесла доходность {report['best_trade']:.2f}%, а худшая — {report['worst_trade']:.2f}%.")
        # Возвращаем сформированные выводы
        return "\n".join(conclusions)

    def analyze_trading_reportv2(self, report):
        conclusions = []
        recommendations = []

        # Анализ прибыли и убытков
        if report["return_percent"] < 0:
            conclusions.append(f"Торговая стратегия показала отрицательный результат с возвратом {report['return_percent']:.2f}% за весь период.")
            recommendations.append("Рассмотрите возможность пересмотра торговой стратегии, так как общая доходность отрицательная.")
        else:
            conclusions.append(f"Торговая стратегия показала положительный результат с возвратом {report['return_percent']:.2f}% за весь период.")
        
        # Годовая доходность
        if report["annual_return"] > 0:
            conclusions.append(f"Годовая доходность составила {report['annual_return']:.2f}%.")
        else:
            conclusions.append("Годовая доходность отрицательная.")
            recommendations.append("Попробуйте сократить убытки или увеличить прибыль, чтобы повысить годовую доходность.")

        # Волатильность
        conclusions.append(f"Годовая волатильность составила {report['annual_volatility']:.2f}%.")
        if report["annual_volatility"] > 20:
            recommendations.append("Высокая волатильность. Рассмотрите возможность использования стратегий, направленных на снижение риска.")

        # Коэффициенты Шарпа, Сортино, Кальмара
        if report["sharpe_ratio"] > 1:
            conclusions.append(f"Коэффициент Шарпа равен {report['sharpe_ratio']:.2f}, что указывает на хорошее соотношение доходности к риску.")
        else:
            conclusions.append(f"Коэффициент Шарпа равен {report['sharpe_ratio']:.2f}, что указывает на низкую доходность по сравнению с риском.")
            recommendations.append("Попробуйте улучшить соотношение доходности к риску, возможно, с помощью диверсификации.")

        if report["sortino_ratio"] > 1:
            conclusions.append(f"Коэффициент Сортино равен {report['sortino_ratio']:.2f}, что указывает на хорошую доходность при управляемом риске.")
        else:
            conclusions.append(f"Коэффициент Сортино равен {report['sortino_ratio']:.2f}, что свидетельствует о высоких убытках по сравнению с ожидаемой доходностью.")
            recommendations.append("Постарайтесь уменьшить негативные отклонения от средней доходности, чтобы повысить коэффициент Сортино.")

        if report["calmar_ratio"] > 1:
            conclusions.append(f"Коэффициент Кальмара равен {report['calmar_ratio']:.2f}, что указывает на благоприятное соотношение доходности к максимальной просадке.")
        else:
            conclusions.append(f"Коэффициент Кальмара равен {report['calmar_ratio']:.2f}, что указывает на значительные потери капитала.")
            recommendations.append("Рассмотрите возможность уменьшения максимальной просадки, возможно, путем уменьшения размера позиции или использования стоп-лоссов.")

        # Максимальная и средняя просадки
        conclusions.append(f"Максимальная просадка составила {report['max_drawdown']:.2f}%, что может указывать на значительные потери капитала.")
        conclusions.append(f"Средняя просадка составила {report['avg_drawdown']:.2f}%.")
        if report["max_drawdown"] > 50:
            recommendations.append("Максимальная просадка очень высока. Подумайте об изменении стратегии, чтобы уменьшить риски.")

        # Фактор прибыли
        if report["profit_factor"] > 1:
            conclusions.append(f"Фактор прибыли составляет {report['profit_factor']:.2f}, что означает, что стратегия была прибыльной.")
        else:
            conclusions.append(f"Фактор прибыли составляет {report['profit_factor']:.2f}, что указывает на то, что стратегия была убыточной.")
            recommendations.append("Убыточная стратегия. Попробуйте улучшить соотношение прибыли к убыткам или снизить операционные расходы.")

        # Процент побед
        conclusions.append(f"Процент побед составил {report['win_rate']:.2f}%.")
        if report["win_rate"] < 50:
            recommendations.append("Низкий процент побед. Рассмотрите возможность улучшения системы входа и выхода из сделок.")

        # Лучшие и худшие сделки
        conclusions.append(f"Лучшая сделка принесла доходность {report['best_trade']:.2f}%, а худшая — {report['worst_trade']:.2f}%.")
        if report["worst_trade"] < -10:
            recommendations.append("Значительные убытки в худшей сделке. Используйте ограничения убытков, такие как стоп-лоссы.")

        # Объединяем выводы и рекомендации
        output = "\n".join(conclusions) + "\n\nРекомендации:\n" + "\n".join(recommendations)
        return output
# Формируем отчет
# report = {
#     'Начало': str(start_date),
#     'Конец': str(end_date),
#     'Продолжительность': str(duration),
#     'Время экспозиции [%]': exposure_time,
#     'Окончательный капитал [$]': final_capital,
#     'Пик капитала [$]': peak_capital,
#     'Возврат [%]': return_percent,
#     'Доходность покупки и удержания [%]': buy_and_hold_return,
#     'Возврат (годовой) [%]': annual_return,
#     'Волатильность (годовая) [%]': annual_volatility,
#     'Коэффициент Шарпа': sharpe_ratio,
#     'Коэффициент Сортино': sortino_ratio,
#     'Коэффициент Кальмара': calmar_ratio,
#     'Макс. просадка [%]': max_drawdown,
#     'Средн. просадка [%]': avg_drawdown,
#     'Макс. продолжительность просадки': max_drawdown_duration,
#     'Средняя продолжительность просадки': avg_drawdown_duration,
#     'Сделки': num_trades,
#     'Процент побед [%]': win_rate,
#     'Лучшая сделка [%]': best_trade,
#     'Худшая сделка [%]': worst_trade,
#     'Средний объем торговли [%]': avg_trade_volume,
#     'Макс. продолжительность торговли': max_trade_duration,
#     'Средняя продолжительность торговли': avg_trade_duration,
#     'Фактор прибыли': profit_factor,
#     'Ожидание [%]': expectation,
#     'SQN': sqn
# }
