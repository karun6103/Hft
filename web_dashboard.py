from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import uvicorn
from datetime import datetime
import json

from config import config
from models import DatabaseManager
from arbitrage_engine import ArbitrageEngine

app = FastAPI(title="Forex Arbitrage Bot Dashboard", version="1.0.0")

# Initialize components
db = DatabaseManager()
engine = ArbitrageEngine()

class DashboardData(BaseModel):
    performance: Dict
    recent_trades: List[Dict]
    recent_opportunities: List[Dict]
    risk_metrics: Dict
    config_summary: Dict

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Main dashboard page"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Forex Arbitrage Bot Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 10px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                text-align: center;
            }
            .content {
                padding: 20px;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 20px;
            }
            .card {
                background: #f8f9fa;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .card h3 {
                margin-top: 0;
                color: #495057;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
            }
            .metric {
                display: flex;
                justify-content: space-between;
                margin: 10px 0;
                padding: 10px;
                background: white;
                border-radius: 5px;
                border-left: 4px solid #667eea;
            }
            .metric.positive { border-left-color: #28a745; }
            .metric.negative { border-left-color: #dc3545; }
            .metric.warning { border-left-color: #ffc107; }
            .refresh-btn {
                background: #667eea;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                margin-bottom: 20px;
            }
            .refresh-btn:hover {
                background: #5a6fd8;
            }
            .status {
                display: inline-block;
                padding: 5px 10px;
                border-radius: 15px;
                font-size: 12px;
                font-weight: bold;
            }
            .status.running { background: #d4edda; color: #155724; }
            .status.stopped { background: #f8d7da; color: #721c24; }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }
            th, td {
                padding: 8px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            th {
                background-color: #f8f9fa;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Forex Arbitrage Bot Dashboard</h1>
                <p>Real-time monitoring and performance tracking</p>
            </div>
            <div class="content">
                <button class="refresh-btn" onclick="loadDashboard()">🔄 Refresh Data</button>
                
                <div class="grid">
                    <div class="card">
                        <h3>📊 Performance Overview</h3>
                        <div id="performance-metrics"></div>
                    </div>
                    
                    <div class="card">
                        <h3>⚠️ Risk Management</h3>
                        <div id="risk-metrics"></div>
                    </div>
                    
                    <div class="card">
                        <h3>⚙️ Configuration</h3>
                        <div id="config-summary"></div>
                    </div>
                    
                    <div class="card">
                        <h3>📈 Profit Chart</h3>
                        <canvas id="profitChart" width="400" height="200"></canvas>
                    </div>
                </div>
                
                <div class="grid">
                    <div class="card">
                        <h3>💼 Recent Trades</h3>
                        <div id="recent-trades"></div>
                    </div>
                    
                    <div class="card">
                        <h3>🔍 Recent Opportunities</h3>
                        <div id="recent-opportunities"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            let profitChart;
            
            async function loadDashboard() {
                try {
                    const response = await fetch('/api/dashboard-data');
                    const data = await response.json();
                    
                    updatePerformanceMetrics(data.performance);
                    updateRiskMetrics(data.risk_metrics);
                    updateConfigSummary(data.config_summary);
                    updateRecentTrades(data.recent_trades);
                    updateRecentOpportunities(data.recent_opportunities);
                    updateProfitChart(data.performance);
                    
                } catch (error) {
                    console.error('Error loading dashboard data:', error);
                }
            }
            
            function updatePerformanceMetrics(performance) {
                const container = document.getElementById('performance-metrics');
                container.innerHTML = `
                    <div class="metric ${performance.net_profit >= 0 ? 'positive' : 'negative'}">
                        <span>Net Profit</span>
                        <span>$${performance.net_profit.toFixed(2)}</span>
                    </div>
                    <div class="metric">
                        <span>Total Trades</span>
                        <span>${performance.total_trades}</span>
                    </div>
                    <div class="metric">
                        <span>Win Rate</span>
                        <span>${performance.win_rate.toFixed(1)}%</span>
                    </div>
                    <div class="metric">
                        <span>Average Profit</span>
                        <span>$${performance.average_profit.toFixed(2)}</span>
                    </div>
                    <div class="metric">
                        <span>Active Trades</span>
                        <span>${performance.active_trades}</span>
                    </div>
                `;
            }
            
            function updateRiskMetrics(risk) {
                const container = document.getElementById('risk-metrics');
                container.innerHTML = `
                    <div class="metric ${risk.daily_loss > 50 ? 'warning' : ''}">
                        <span>Daily Loss</span>
                        <span>$${risk.daily_loss.toFixed(2)}</span>
                    </div>
                    <div class="metric ${risk.max_drawdown > 0.05 ? 'warning' : ''}">
                        <span>Max Drawdown</span>
                        <span>${(risk.max_drawdown * 100).toFixed(2)}%</span>
                    </div>
                    <div class="metric">
                        <span>Active Trades</span>
                        <span>${risk.active_trades}</span>
                    </div>
                    <div class="metric">
                        <span>Current Balance</span>
                        <span>$${risk.current_balance.toFixed(2)}</span>
                    </div>
                `;
            }
            
            function updateConfigSummary(config) {
                const container = document.getElementById('config-summary');
                container.innerHTML = `
                    <div class="metric">
                        <span>Exchanges</span>
                        <span>${config.exchanges}</span>
                    </div>
                    <div class="metric">
                        <span>Trading Pairs</span>
                        <span>${config.trading_pairs}</span>
                    </div>
                    <div class="metric">
                        <span>Min Profit Threshold</span>
                        <span>${config.min_profit_threshold}%</span>
                    </div>
                    <div class="metric">
                        <span>Max Position Size</span>
                        <span>$${config.max_position_size}</span>
                    </div>
                `;
            }
            
            function updateRecentTrades(trades) {
                const container = document.getElementById('recent-trades');
                if (trades.length === 0) {
                    container.innerHTML = '<p>No recent trades</p>';
                    return;
                }
                
                let html = '<table><thead><tr><th>Time</th><th>Pair</th><th>Profit</th><th>Status</th></tr></thead><tbody>';
                trades.forEach(trade => {
                    const profitClass = trade.profit >= 0 ? 'positive' : 'negative';
                    html += `
                        <tr>
                            <td>${new Date(trade.timestamp).toLocaleTimeString()}</td>
                            <td>${trade.pair}</td>
                            <td class="${profitClass}">$${trade.profit.toFixed(2)}</td>
                            <td><span class="status ${trade.status}">${trade.status}</span></td>
                        </tr>
                    `;
                });
                html += '</tbody></table>';
                container.innerHTML = html;
            }
            
            function updateRecentOpportunities(opportunities) {
                const container = document.getElementById('recent-opportunities');
                if (opportunities.length === 0) {
                    container.innerHTML = '<p>No recent opportunities</p>';
                    return;
                }
                
                let html = '<table><thead><tr><th>Time</th><th>Pair</th><th>Profit %</th><th>Exchanges</th></tr></thead><tbody>';
                opportunities.forEach(opp => {
                    html += `
                        <tr>
                            <td>${new Date(opp.timestamp).toLocaleTimeString()}</td>
                            <td>${opp.pair}</td>
                            <td>${opp.profit_percentage.toFixed(2)}%</td>
                            <td>${opp.exchange1} → ${opp.exchange2}</td>
                        </tr>
                    `;
                });
                html += '</tbody></table>';
                container.innerHTML = html;
            }
            
            function updateProfitChart(performance) {
                const ctx = document.getElementById('profitChart').getContext('2d');
                
                if (profitChart) {
                    profitChart.destroy();
                }
                
                profitChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: ['Total Profit', 'Total Loss', 'Net Profit'],
                        datasets: [{
                            label: 'Profit/Loss ($)',
                            data: [
                                performance.total_profit,
                                performance.total_loss,
                                performance.net_profit
                            ],
                            backgroundColor: ['#28a745', '#dc3545', '#007bff'],
                            borderColor: ['#28a745', '#dc3545', '#007bff'],
                            borderWidth: 2
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            }
            
            // Load dashboard on page load
            document.addEventListener('DOMContentLoaded', loadDashboard);
            
            // Auto-refresh every 30 seconds
            setInterval(loadDashboard, 30000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/api/dashboard-data")
async def get_dashboard_data():
    """Get dashboard data"""
    try:
        # Get performance data
        performance = engine.get_performance_summary()
        
        # Get recent trades
        recent_trades = db.get_recent_trades(10)
        trades_data = []
        for trade in recent_trades:
            trades_data.append({
                'timestamp': trade.timestamp.isoformat(),
                'pair': trade.pair,
                'profit': trade.net_profit,
                'status': trade.status
            })
        
        # Get recent opportunities
        recent_opportunities = db.get_recent_opportunities(10)
        opportunities_data = []
        for opp in recent_opportunities:
            opportunities_data.append({
                'timestamp': opp.timestamp.isoformat(),
                'pair': opp.pair,
                'profit_percentage': opp.profit_percentage,
                'exchange1': opp.exchange1,
                'exchange2': opp.exchange2
            })
        
        # Get risk metrics
        risk_metrics = engine.risk_manager.get_risk_metrics()
        
        # Get config summary
        config_summary = {
            'exchanges': len(config.exchanges),
            'trading_pairs': len(config.trading_pairs),
            'min_profit_threshold': config.arbitrage.min_profit_threshold * 100,
            'max_position_size': config.arbitrage.max_position_size
        }
        
        return DashboardData(
            performance=performance['daily_stats'],
            recent_trades=trades_data,
            recent_opportunities=opportunities_data,
            risk_metrics=risk_metrics,
            config_summary=config_summary
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def get_status():
    """Get bot status"""
    return {
        "status": "running" if engine.running else "stopped",
        "timestamp": datetime.now().isoformat(),
        "uptime": "N/A"  # Could be calculated from start time
    }

@app.post("/api/start")
async def start_bot():
    """Start the arbitrage bot"""
    try:
        if not engine.running:
            # Start the bot in background
            asyncio.create_task(engine.start())
            return {"message": "Bot started successfully"}
        else:
            return {"message": "Bot is already running"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stop")
async def stop_bot():
    """Stop the arbitrage bot"""
    try:
        if engine.running:
            engine.stop()
            return {"message": "Bot stopped successfully"}
        else:
            return {"message": "Bot is already stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)