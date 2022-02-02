import React from 'react';

export const Icon = ({ icon, color = "black" }) => {
  return (
    <i className={`fa fa-${icon} text-${color}`}></i>
  );
}
