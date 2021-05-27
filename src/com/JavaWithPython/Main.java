/*
 * @Descripttion: 
 * @Version: xxx
 * @Author: WanJu
 * @Date: 2021-05-24 20:34:44
 * @LastEditors: WanJu
 * @LastEditTime: 2021-05-26 17:25:25
 */
package com.JavaWithPython;
import java.util.Scanner;

import com.alibaba.fastjson.JSONObject;

public class Main {
    public static void main(String[] args) {
        String cmd = "";
        Scanner input = new Scanner(System.in);
        while (!cmd.equalsIgnoreCase("exit")) {
            System.out.print("1: DataPreProcess\n" +
                                "2: GetTrainData\n" + 
                                "3: Train\n" +
                                "4: Predict\n" +
                                ">>> ");
            cmd = input.next();
            if (!cmd.matches("[0-9]+")) {
                continue;
            }
            switch (Integer.valueOf(cmd)){
                case 1:
                    DiskPredict.DataPreProcess("\"2016\"", 0);
                    break;
                case 2:
                    DiskPredict.GetTrainData("\"2016\"", 1.0f/3, 0.1f);
                    break;
                case 3:
                    JSONObject params = new JSONObject();
                    params.put("max_depth", new int[]{10, 20, 30});
                    params.put("max_features", new int[]{4, 7, 10});
                    params.put("n_estimators", new int[]{10, 20, 30, 40});
                    
                    DiskPredict.Train("\"2016\"", "\"ST4000DM000\"", params);
                    break;
                case 4:
                    DiskPredict.Predict("\"E:\\BackBlaze\\DP_test\\data_to_predict\"");
                    break;
                default:
                    System.out.println("没有该函数！");
                    break;
            }
        }
        input.close();
    }
}