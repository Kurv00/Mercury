var{
x: 10;
y: 3;
msg: "This is KurvScript!";
}

<printnl>{msg}</printnl>
<calc>x * y + 5</calc>

<if condition="x > y">
  <printnl>{x} is greater than {y}</printnl>
</if>

<for var="i" in="(1, 5)">
  <printnl>Value: {i}</printnl>
</for>
