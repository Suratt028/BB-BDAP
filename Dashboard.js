import React, { useEffect, useState } from "react";
import { View, Text, ScrollView, Button } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { VictoryLine, VictoryChart } from "victory-native";

export default function Dashboard({ setIsLoggedIn }) {
  const [data, setData] = useState([]);
  const [kpi, setKpi] = useState({});

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    const token = await AsyncStorage.getItem("token");

    const kpiRes = await fetch("http://192.168.1.45:5000/dashboard", {
      headers: { Authorization: token }
    });
    const kpiData = await kpiRes.json();
    setKpi(kpiData);

    const salesRes = await fetch("http://192.168.1.45:5000/sales", {
      headers: { Authorization: token }
    });
    const salesData = await salesRes.json();

    const formatted = salesData.map(item => ({
      x: item.date,
      y: item.sales
    }));

    setData(formatted);
  };

  const logout = async () => {
    await AsyncStorage.removeItem("token");
    setIsLoggedIn(false);
  };

  return (
    <ScrollView style={{ padding: 20 }}>
      <Text style={{ fontSize: 20 }}>Dashboard</Text>
      <Text>Total Sales: {kpi.total_sales}</Text>
      <Text>Total Orders: {kpi.total_orders}</Text>
      <Text>Avg Order: {kpi.average_order}</Text>

      <VictoryChart>
        <VictoryLine data={data} />
      </VictoryChart>

      <Button title="Logout" onPress={logout} />
    </ScrollView>
  );
}
